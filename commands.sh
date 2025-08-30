aws logs tail /aws/lambda/ai-automation-course-registration-handler--follow


aws logs tail /aws/lambda/ai-automation-course-payment-webhook



cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ../


aws logs tail "/aws/lambda/ai-automation-course-payment-webhook" --since 48h --follow



aws dynamodb scan --table-name course_registrations --attributes-to-get "id" --query "Items[].id.S" --output text | tr '\t' '\n' | xargs -I {} aws dynamodb delete-item --table-name registration --key '{"id":{"S":"{}"}}'



ppp  pytest test/integration/test_lambda_health.py -v   

aws dynamodb scan --table-name course_registrations --query "Items[*].{Name:name.S, Email:email.S, PaymentStatus:payment_status.S}" --output table  
