#!/bin/bash

# Build script for Lambda functions with dependencies

set -e

echo "Building Lambda deployment packages..."

# Function to build a Lambda package
build_lambda() {
    local function_name=$1
    local source_file=$2
    
    echo "Building ${function_name}..."
    
    # Create temp directory
    rm -rf /tmp/${function_name}
    mkdir -p /tmp/${function_name}
    
    # Install dependencies if requirements.txt exists
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt -t /tmp/${function_name}/ --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11
    fi
    
    # Copy the Lambda function code
    cp ${source_file} /tmp/${function_name}/lambda_function.py
    
    # Create the zip file
    cd /tmp/${function_name}
    zip -r9 ${OLDPWD}/${function_name}.zip .
    cd ${OLDPWD}
    
    # Clean up
    rm -rf /tmp/${function_name}
    
    echo "✓ ${function_name}.zip created"
}

# Build payment-webhook with Stripe dependency
build_lambda "payment-webhook" "payment-webhook.py"

# Build registration-handler (no external dependencies needed, boto3 is in Lambda runtime)
build_lambda "registration-handler" "registration-handler.py"

echo "All Lambda packages built successfully!"