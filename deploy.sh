#!/bin/bash

# Check for --tfonly flag
if [[ "$1" == "--tfonly" ]]; then
    echo "Skipping Python build (--tfonly flag detected)"
else
    cd lambda && ./build_lambda_package.sh; cd ..
fi

cd tf && terraform apply -auto-approve; cd ..
cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ..