#!/bin/bash

# Build script for Lambda functions with dependencies

set -e

echo "Building Lambda deployment packages..."

# Cache directory for pip dependencies
CACHE_DIR="/tmp/lambda-deps-cache"
mkdir -p ${CACHE_DIR}

# Function to get checksum of requirements file
get_requirements_checksum() {
    if [ -f requirements.txt ]; then
        sha256sum requirements.txt | cut -d' ' -f1
    else
        echo "no-requirements"
    fi
}

# Function to build a Lambda package
build_lambda() {
    local function_name=$1
    local source_file=$2
    
    echo "Building ${function_name}..."
    
    # Create temp directory
    rm -rf /tmp/${function_name}
    mkdir -p /tmp/${function_name}
    
    # Check if requirements.txt exists and handle caching
    if [ -f requirements.txt ]; then
        local req_checksum=$(get_requirements_checksum)
        local cache_path="${CACHE_DIR}/${function_name}-${req_checksum}"
        
        if [ -d "${cache_path}" ]; then
            echo "  Using cached dependencies from ${cache_path}"
            cp -r ${cache_path}/* /tmp/${function_name}/
        else
            echo "  Installing dependencies (requirements changed or first run)..."
            pip install -r requirements.txt -t /tmp/${function_name}/ --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11
            
            # Cache the installed dependencies
            echo "  Caching dependencies to ${cache_path}"
            rm -rf ${cache_path}
            mkdir -p ${cache_path}
            cp -r /tmp/${function_name}/* ${cache_path}/
        fi
    fi
    
    # Copy the Lambda function code
    cp ${source_file} /tmp/${function_name}/lambda_function.py
    
    # Copy email_templates.py if it exists
    if [ -f email_templates.py ]; then
        cp email_templates.py /tmp/${function_name}/
    fi
    
    # Copy meta_conversions_api.py if it exists (needed for Meta tracking)
    if [ -f meta_conversions_api.py ]; then
        cp meta_conversions_api.py /tmp/${function_name}/
    fi
    
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

# Build contact-handler (no external dependencies needed, boto3 is in Lambda runtime)
build_lambda "contact-handler" "contact-handler.py"

# Build view-content-handler (needs requests for Meta API calls)
# build_lambda "view-content-handler" "view_content_handler.py"

# Build application_handler (needs requests for Meta API calls)
build_lambda "application_handler" "application_handler.py"

# Build referral-handler (no external dependencies needed, boto3 is in Lambda runtime)
build_lambda "referral-handler" "referral-handler.py"

echo "All Lambda packages built successfully!"