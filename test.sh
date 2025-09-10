#!/bin/bash

# Check if --slow argument is provided
SLOW_TESTS=false
if [[ "$1" == "--slow" ]]; then
    SLOW_TESTS=true
fi


# Run slow integration tests if --slow flag is provided
if [[ "$SLOW_TESTS" == "true" ]]; then
    ppp pytest test/slow
else
    ppp pytest lambda
    ppp pytest test/integration
fi