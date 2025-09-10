#!/bin/bash

# Check arguments
SLOW_TESTS=false
HEADLESS_MODE=true

# Parse arguments
for arg in "$@"; do
    case $arg in
        --slow)
            SLOW_TESTS=true
            ;;
        --head)
            HEADLESS_MODE=false
            ;;
    esac
done

# Run slow integration tests if --slow flag is provided
if [[ "$SLOW_TESTS" == "true" ]]; then
    if [[ "$HEADLESS_MODE" == "false" ]]; then
        HEADLESS=false ppp pytest test/slow
    else
        ppp pytest test/slow
    fi
else
    ppp pytest lambda
    ppp pytest test/integration
fi