#!/bin/bash
# Convenience script to run pre-commit with custom config location

CONFIG_PATH="tools/pre-commit-config.yaml"

case "$1" in
    "install")
        poetry run pre-commit install --config $CONFIG_PATH
        ;;
    "run")
        poetry run pre-commit run --all-files --config $CONFIG_PATH
        ;;
    "update")
        poetry run pre-commit autoupdate --config $CONFIG_PATH
        ;;
    *)
        echo "Usage: $0 {install|run|update}"
        echo "  install - Install pre-commit hooks"
        echo "  run     - Run pre-commit on all files"
        echo "  update  - Update hook versions"
        ;;
esac 