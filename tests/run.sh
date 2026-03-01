#!/usr/bin/env bash
# Launcher for trigger-test-api.mjs — pass all args through
exec node "$(dirname "$0")/trigger-test-api.mjs" "$@"
