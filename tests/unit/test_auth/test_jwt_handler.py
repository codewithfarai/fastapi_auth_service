import pytest
from jose import jwt, JWTError, ExpiredSignatureError, JWTClaimsError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.core.auth.jwt_handler import JWTHandler
from app.config import Settings # For type hinting test_settings
# Import fixtures from conftest.py (pytest will inject them)
# test_settings, test_user_data, create_test_token (though we might use handler.encode directly)

# Helper to extract token string if header fixtures were used (not strictly needed if we craft tokens directly)
def extract_token_from_header(header: dict) -> str:
    return header["Authorization"].split(" ")[1]

@pytest.fixture
def jwt_handler(test_settings: Settings) -> JWTHandler:
    # The JWTHandler class is hardcoded to HS256 and uses settings.secret_key.
    # We need to ensure the JWTHandler uses a consistent secret key for tests.
    # The conftest.py create_test_token uses "test-secret" by default.
    # test_settings.secret_key from conftest.py is "test-secret-key-for-testing-only".
    # To avoid conflicts and ensure handler tests are self-contained regarding keys:
    settings_for_handler = test_settings.copy(deep=True)
    # Let's use a distinct secret for this handler's tests to be very explicit.
    settings_for_handler.secret_key = "jwt-handler-specific-test-secret"

    # Ensure issuer and audience are also aligned if tokens are to be cross-validated.
    # JWTHandler uses settings.auth0_api_audience and f"https://{settings.auth0_domain}/"
    # These are taken from test_settings, which are:
    # auth0_domain="test.auth0.com" -> iss="https://test.auth0.com/"
    # auth0_api_audience="https://test-api.example.com"
    # This setup is fine.
    return JWTHandler(settings=settings_for_handler)

@pytest.fixture
def sample_payload(test_user_data: dict) -> dict:
    # test_user_data already includes 'sub', 'name', 'email', 'roles', 'permissions'
    # JWTHandler.encode_token requires 'sub'.
    payload = test_user_data.copy()
    # Ensure essential claims for testing are present, like 'sub'
    if "sub" not in payload:
        payload["sub"] = "test-subject-123"
    return payload

# --- Encode Tests ---
def test_encode_token_success(jwt_handler: JWTHandler, sample_payload: dict):
    token = jwt_handler.encode_token(sample_payload)
    assert isinstance(token, str)

    decoded_by_jose = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm], audience=jwt_handler.audience, issuer=jwt_handler.issuer)

    assert decoded_by_jose["sub"] == sample_payload["sub"]
    assert decoded_by_jose["aud"] == jwt_handler.audience
    assert decoded_by_jose["iss"] == jwt_handler.issuer
    assert "exp" in decoded_by_jose
    assert "iat" in decoded_by_jose
    assert decoded_by_jose["exp"] > decoded_by_jose["iat"]

def test_encode_token_custom_expiry(jwt_handler: JWTHandler, sample_payload: dict):
    custom_delta = timedelta(hours=2)
    # Record time before encoding
    time_before_encoding = datetime.now(timezone.utc)
    token = jwt_handler.encode_token(sample_payload, expires_delta=custom_delta)

    decoded_by_jose = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])

    # Expected 'iat' should be very close to time_before_encoding
    iat_datetime = datetime.fromtimestamp(decoded_by_jose["iat"], tz=timezone.utc)
    assert abs(iat_datetime - time_before_encoding) < timedelta(seconds=5)

    # Expected 'exp' based on actual 'iat' from token
    expected_exp_datetime = iat_datetime + custom_delta
    exp_datetime = datetime.fromtimestamp(decoded_by_jose["exp"], tz=timezone.utc)
    assert abs(exp_datetime - expected_exp_datetime) < timedelta(seconds=5)


def test_encode_token_missing_sub_raises_error(jwt_handler: JWTHandler):
    payload_no_sub = {"name": "Test User", "email": "no-sub@example.com"}
    with pytest.raises(ValueError, match="Payload must contain 'sub'"):
        jwt_handler.encode_token(payload_no_sub)

# --- Decode Tests ---
def test_decode_valid_token(jwt_handler: JWTHandler, sample_payload: dict):
    token = jwt_handler.encode_token(sample_payload)

    decoded_payload = jwt_handler.decode_token(token)
    assert decoded_payload["sub"] == sample_payload["sub"]
    assert decoded_payload["aud"] == jwt_handler.audience
    assert decoded_payload["iss"] == jwt_handler.issuer

def test_decode_expired_token(jwt_handler: JWTHandler, sample_payload: dict):
    expired_token = jwt_handler.encode_token(sample_payload, expires_delta=timedelta(seconds=-10)) # Ensure it's well expired

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(expired_token)
    assert excinfo.value.status_code == 401
    assert "Token has expired" in excinfo.value.detail

def test_decode_invalid_signature_token(jwt_handler: JWTHandler, sample_payload: dict):
    wrong_key = "this-is-not-the-correct-secret-key-for-sure"
    # Construct all claims the handler's decode method will expect
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(minutes=15)
    claims_for_wrong_key_token = {
        **sample_payload,
        "exp": exp,
        "iat": iat,
        "iss": jwt_handler.issuer,
        "aud": jwt_handler.audience
    }
    token_wrong_signature = jwt.encode(claims_for_wrong_key_token, wrong_key, algorithm=jwt_handler.algorithm)

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_wrong_signature)
    assert excinfo.value.status_code == 401
    assert "Invalid token: Signature verification failed" in excinfo.value.detail

def test_decode_invalid_issuer_token(jwt_handler: JWTHandler, sample_payload: dict):
    invalid_issuer = "https://invalid.issuer.com/"
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(minutes=15)
    token_invalid_issuer = jwt.encode(
        {**sample_payload, "exp": exp, "iat": iat, "iss": invalid_issuer, "aud": jwt_handler.audience },
        jwt_handler.secret_key,
        algorithm=jwt_handler.algorithm
    )

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_invalid_issuer)
    assert excinfo.value.status_code == 401
    assert "Token claims validation failed: Invalid issuer" in excinfo.value.detail

def test_decode_invalid_audience_token(jwt_handler: JWTHandler, sample_payload: dict):
    invalid_audience = "invalid-audience-for-sure"
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(minutes=15)
    token_invalid_audience = jwt.encode(
        {**sample_payload, "exp": exp, "iat": iat, "iss": jwt_handler.issuer, "aud": invalid_audience},
        jwt_handler.secret_key,
        algorithm=jwt_handler.algorithm
    )

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_invalid_audience)
    assert excinfo.value.status_code == 401
    assert "Token claims validation failed: Invalid audience" in excinfo.value.detail

def test_decode_malformed_token(jwt_handler: JWTHandler):
    malformed_token = "this.is.not.a.valid.jwt.token"
    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(malformed_token)
    assert excinfo.value.status_code == 401
    assert "Invalid token: Not enough segments" in excinfo.value.detail # Common jose error for this

def test_decode_token_missing_exp_claim(jwt_handler: JWTHandler, sample_payload: dict):
    iat = datetime.now(timezone.utc)
    # exp claim is mandatory for python-jose decode by default
    payload_no_exp = {**sample_payload, "iat": iat, "iss": jwt_handler.issuer, "aud": jwt_handler.audience}
    # Remove 'exp' if it was in sample_payload (it shouldn't be, encode_token adds it)
    payload_no_exp.pop("exp", None)
    token_no_exp = jwt.encode(payload_no_exp, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_no_exp)
    assert excinfo.value.status_code == 401
    # python-jose raises JWTError -> "Missing required claim: exp" if options don't disable verify_exp
    # which then becomes JWTClaimsError in the decode function for missing claims like 'exp'
    assert "Token claims validation failed: Missing required claim: exp" in excinfo.value.detail


def test_decode_token_iat_in_future(jwt_handler: JWTHandler, sample_payload: dict):
    future_iat = datetime.now(timezone.utc) + timedelta(minutes=10)
    future_exp = future_iat + timedelta(minutes=5)

    token_future_iat = jwt.encode(
        {**sample_payload, "exp": future_exp, "iat": future_iat, "iss": jwt_handler.issuer, "aud": jwt_handler.audience },
        jwt_handler.secret_key,
        algorithm=jwt_handler.algorithm
    )

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_future_iat)
    assert excinfo.value.status_code == 401
    assert "Token claims validation failed: The token was issued in the future" in excinfo.value.detail

def test_decode_token_nbf_in_future(jwt_handler: JWTHandler, sample_payload: dict):
    nbf_future = datetime.now(timezone.utc) + timedelta(minutes=10)
    iat_now = datetime.now(timezone.utc)
    exp_valid = iat_now + timedelta(minutes=15)

    token_nbf_future = jwt.encode(
        {**sample_payload, "exp": exp_valid, "iat": iat_now, "nbf": nbf_future, "iss": jwt_handler.issuer, "aud": jwt_handler.audience },
        jwt_handler.secret_key,
        algorithm=jwt_handler.algorithm
    )

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_nbf_future)
    assert excinfo.value.status_code == 401
    assert "Token claims validation failed: The token is not yet active" in excinfo.value.detail

def test_decode_token_nbf_passed(jwt_handler: JWTHandler, sample_payload: dict):
    nbf_past = datetime.now(timezone.utc) - timedelta(minutes=10)
    iat_now = datetime.now(timezone.utc)
    exp_valid = iat_now + timedelta(minutes=15)

    token_nbf_past = jwt.encode(
        {**sample_payload, "exp": exp_valid, "iat": iat_now, "nbf": nbf_past, "iss": jwt_handler.issuer, "aud": jwt_handler.audience },
        jwt_handler.secret_key,
        algorithm=jwt_handler.algorithm
    )

    decoded_payload = jwt_handler.decode_token(token_nbf_past)
    assert decoded_payload["sub"] == sample_payload["sub"]

def test_decode_token_missing_sub_is_valid(jwt_handler: JWTHandler):
    # Verifies that JWTHandler.decode_token itself doesn't require 'sub'.
    # 'sub' requirement is usually an application-level check after decoding.
    minimal_payload = {
        # "sub": "anything", # Deliberately missing
        "user_id_alt": "alt-user-123", # Some other identifier
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "iat": datetime.now(timezone.utc),
        "iss": jwt_handler.issuer,
        "aud": jwt_handler.audience
    }
    token_no_sub = jwt.encode(minimal_payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)
    decoded_payload = jwt_handler.decode_token(token_no_sub)
    assert "user_id_alt" in decoded_payload
    assert "sub" not in decoded_payload
    # This is fine, the token is valid as per JWT structure and claims validation (iss, aud, exp, nbf, iat)
    # The application using the decoded payload would then check for 'sub' if it needs it.

# Example of testing a token that might be missing 'iat'
def test_decode_token_missing_iat_claim(jwt_handler: JWTHandler, sample_payload: dict):
    # python-jose's decode also checks for 'iat' by default.
    payload_no_iat = {
        **sample_payload,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "iss": jwt_handler.issuer,
        "aud": jwt_handler.audience
    }
    payload_no_iat.pop("iat", None) # Ensure 'iat' is not there
    token_no_iat = jwt.encode(payload_no_iat, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)

    with pytest.raises(HTTPException) as excinfo:
        jwt_handler.decode_token(token_no_iat)
    assert excinfo.value.status_code == 401
    assert "Token claims validation failed: Missing required claim: iat" in excinfo.value.detail
