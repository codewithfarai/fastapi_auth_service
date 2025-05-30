# verify_setup.py
"""
Project setup verification script - Updated for correct structure
"""

import os
import sys
import asyncio
from pathlib import Path


def verify_file_structure():
    """Verify all required files exist based on actual project structure"""
    print("📋 Verifying file structure...")
    
    required_files = [
        # Root app files
        'app/__init__.py',
        'app/main.py',
        'app/config.py',
        
        # API routes structure
        'app/api/__init__.py',
        'app/api/routes/__init__.py',
        'app/api/routes/auth.py',
        'app/api/routes/customer.py',
        'app/api/routes/provider.py',
        'app/api/routes/shared.py',
        'app/api/routes/admin.py',
        
        # API middleware structure
        'app/api/middleware/__init__.py',
        'app/api/middleware/auth.py',
        'app/api/middleware/cors.py',
        'app/api/middleware/logging.py',
        'app/api/middleware/rate_limiting.py',
        
        # Core structure
        'app/core/__init__.py',
        
        # Core auth structure
        'app/core/auth/__init__.py',
        'app/core/auth/jwt_handler.py',
        'app/core/auth/auth0_client.py',
        'app/core/auth/permissions.py',
        
        # Core security structure
        'app/core/security/__init__.py',
        'app/core/security/dependencies.py',
        'app/core/security/roles.py',
        'app/core/security/permissions.py',
        
        # Tests
        'tests/__init__.py',
        'tests/test_main.py',
        
        # Config files
        'run_dev_server.py',
        '.env.example'
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
            existing_files.append(file_path)
        else:
            print(f"  ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    print(f"\n📊 Structure Summary:")
    print(f"  ✅ Existing files: {len(existing_files)}")
    print(f"  ❌ Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"    - {file}")
        return False
    else:
        print("\n✅ All required files present")
        return True


def verify_directory_structure():
    """Verify all required directories exist"""
    print("📁 Verifying directory structure...")
    
    required_directories = [
        'app',
        'app/api',
        'app/api/routes',
        'app/api/middleware',
        'app/core',
        'app/core/auth',
        'app/core/security',
        'tests',
        'docs',
        'monitoring',
        'scripts'
    ]
    
    existing_dirs = []
    missing_dirs = []
    
    for dir_path in required_directories:
        if os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/")
            existing_dirs.append(dir_path)
        else:
            print(f"  ❌ {dir_path}/ (missing)")
            missing_dirs.append(dir_path)
    
    print(f"\n📊 Directory Summary:")
    print(f"  ✅ Existing directories: {len(existing_dirs)}")
    print(f"  ❌ Missing directories: {len(missing_dirs)}")
    
    if missing_dirs:
        print(f"\n⚠️  Missing {len(missing_dirs)} required directories:")
        for dir_path in missing_dirs:
            print(f"    - {dir_path}/")
        return False
    else:
        print("\n✅ All required directories present")
        return True


def create_missing_structure():
    """Create missing directories and __init__.py files"""
    print("🏗️  Creating missing structure...")
    
    # Create directories
    directories = [
        'app/api',
        'app/api/routes',
        'app/api/middleware',
        'app/core',
        'app/core/auth',
        'app/core/security',
        'tests',
        'docs',
        'monitoring',
        'scripts'
    ]
    
    for dir_path in directories:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"  📁 Created directory: {dir_path}/")
    
    # Create __init__.py files
    init_files = [
        'app/__init__.py',
        'app/api/__init__.py',
        'app/api/routes/__init__.py',
        'app/api/middleware/__init__.py',
        'app/core/__init__.py',
        'app/core/auth/__init__.py',
        'app/core/security/__init__.py',
        'tests/__init__.py',
        'docs/__init__.py',
        'monitoring/__init__.py',
        'scripts/__init__.py'
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                # Write appropriate __init__.py content
                module_name = init_file.replace('/', '.').replace('__init__.py', '').rstrip('.')
                f.write(f'"""\n{module_name} module\n"""\n')
            print(f"  📝 Created: {init_file}")


def verify_python_imports():
    """Verify that all modules can be imported correctly"""
    print("🔍 Verifying Python package structure...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Test basic imports
        import app
        print("  ✅ app module imports successfully")
        
        import app.config
        print("  ✅ app.config module imports successfully")
        
        from app.config import settings
        print(f"  ✅ settings loaded - environment: {settings.environment}")
        
        # Test API structure imports
        try:
            import app.api
            print("  ✅ app.api module imports successfully")
        except ImportError:
            print("  ⚠️  app.api module not found (may not be created yet)")
        
        try:
            import app.api.routes
            print("  ✅ app.api.routes module imports successfully")
        except ImportError:
            print("  ⚠️  app.api.routes module not found (may not be created yet)")
        
        try:
            import app.core
            print("  ✅ app.core module imports successfully")
        except ImportError:
            print("  ⚠️  app.core module not found (may not be created yet)")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_fastapi_startup():
    """Test that the FastAPI application starts correctly"""
    print("🚀 Testing FastAPI application startup...")
    
    try:
        # Import the app
        from app.main import app
        from app.config import settings
        
        print("  ✅ FastAPI app imported successfully")
        print(f"  ✅ Environment: {settings.environment}")
        print(f"  ✅ Debug mode: {settings.debug}")
        print(f"  ✅ Auth0 Domain: {settings.auth0_domain}")
        
        # Test that app has the expected attributes
        assert hasattr(app, 'routes'), "App should have routes"
        assert app.title == settings.app_name, "App title mismatch"
        
        # Count routes
        route_count = len(app.routes)
        print(f"  ✅ Routes registered: {route_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI startup error: {e}")
        return False


def run_basic_tests():
    """Run basic endpoint tests"""
    print("🧪 Running basic endpoint tests...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        data = response.json()
        assert "service" in data, "Root response missing service field"
        print("  ✅ Root endpoint (/) working")
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
        data = response.json()
        assert "status" in data, "Health response missing status field"
        print("  ✅ Health endpoint (/health) working")
        
        # Test readiness endpoint
        response = client.get("/ready")
        assert response.status_code == 200, f"Readiness endpoint failed: {response.status_code}"
        print("  ✅ Readiness endpoint (/ready) working")
        
        # Test liveness endpoint
        response = client.get("/live")
        assert response.status_code == 200, f"Liveness endpoint failed: {response.status_code}"
        print("  ✅ Liveness endpoint (/live) working")
        
        # Test OpenAPI docs (if debug mode)
        if hasattr(app, 'docs_url') and app.docs_url:
            response = client.get("/docs")
            assert response.status_code == 200, f"Docs endpoint failed: {response.status_code}"
            print("  ✅ API docs (/docs) accessible")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic tests failed: {e}")
        return False


def check_environment_file():
    """Check if .env file exists and has basic configuration"""
    print("⚙️  Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ⚠️  .env file not found - using defaults")
        if os.path.exists('.env.example'):
            print("  💡 You can copy .env.example to .env and customize")
        return True
    else:
        print("  ✅ .env file found")
        
        # Check for basic required variables
        with open('.env', 'r') as f:
            env_content = f.read()
            
        required_vars = ['SECRET_KEY', 'ENVIRONMENT', 'AUTH0_DOMAIN', 'AUTH0_CLIENT_ID']
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
            else:
                # Check for placeholder values
                for line in env_content.split('\n'):
                    if line.startswith(f'{var}='):
                        value = line.split('=', 1)[1].strip()
                        if 'your-' in value or 'example' in value or 'placeholder' in value:
                            placeholder_vars.append(var)
                        break
        
        if missing_vars:
            print(f"  ⚠️  Missing environment variables: {', '.join(missing_vars)}")
        
        if placeholder_vars:
            print(f"  ⚠️  Placeholder values detected: {', '.join(placeholder_vars)}")
            print("      Please update these with actual values")
        
        if not missing_vars and not placeholder_vars:
            print("  ✅ Environment variables properly configured")
        
        return True


def main():
    """Main verification function"""
    print("🎯 FastAPI Authentication Service - Setup Verification")
    print("=" * 60)
    print("📋 Checking project structure against actual requirements...")
    print()
    
    success = True
    
    # Step 1: Verify directory structure
    if not verify_directory_structure():
        print("\n🏗️  Some directories are missing. Creating them...")
        create_missing_structure()
        print("✅ Missing structure created")
    
    print()
    
    # Step 2: Verify file structure
    if not verify_file_structure():
        success = False
        print("\n💡 To create missing files, you can:")
        print("   1. Create them manually following the structure")
        print("   2. Use the code artifacts provided earlier")
        print("   3. Run individual creation scripts")
    
    print()
    
    # Step 3: Check environment
    if not check_environment_file():
        success = False
    
    print()
    
    # Step 4: Verify Python imports (only if basic files exist)
    if os.path.exists('app/main.py') and os.path.exists('app/config.py'):
        if not verify_python_imports():
            success = False
        
        print()
        
        # Step 5: Test FastAPI startup
        if not test_fastapi_startup():
            success = False
        
        print()
        
        # Step 6: Run basic tests
        if not run_basic_tests():
            success = False
    else:
        print("⚠️  Skipping import and startup tests - core files missing")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! FastAPI Authentication Service setup verified")
        print("\nNext steps:")
        print("1. Update .env with your Auth0 credentials")
        print("2. Start the server: poetry run python run_dev_server.py")
        print("3. Visit: http://localhost:8000")
        print("4. API docs: http://localhost:8000/docs")
        print("5. Run tests: poetry run pytest")
    else:
        print("❌ SETUP INCOMPLETE - Please fix the issues above")
        print("\nCommon fixes:")
        print("1. Create missing files using the provided code artifacts")
        print("2. Ensure all __init__.py files are present")
        print("3. Update .env file with actual Auth0 credentials")
        print("4. Check that all imports work correctly")
    
    return success


if __name__ == "__main__":
    main()