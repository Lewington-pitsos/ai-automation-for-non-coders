#!/bin/bash

# Check for --frontend flag
if [[ "$1" == "--frontend" ]]; then
    echo "Deploying frontend only..."
    cd frontend-tf && terraform apply -auto-approve; cd ..
    exit 0
fi

# Check for --tfonly flag
if [[ "$1" == "--tfonly" ]]; then
    echo "Skipping Python build (--tfonly flag detected)"
else
    cd lambda && ./build_lambda_package.sh; cd ..
fi

cd tf && terraform apply -auto-approve; cd ..
cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ..
cd frontend-tf && terraform apply -auto-approve; cd ..