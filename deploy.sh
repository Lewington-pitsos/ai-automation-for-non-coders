cd lambda && ./build_lambda_package.sh; cd ..
cd tf && terraform apply -auto-approve; cd ..
cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ..