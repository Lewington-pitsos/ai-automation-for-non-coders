aws logs tail /aws/lambda/ai-automation-course-registration-handler--follow


aws logs tail /aws/lambda/ai-automation-course-payment-webhook


aws logs filter-log-events --log-group-name /aws/lambda/ai-automation-course-payment-webhook --start-time 1724774400000


cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ../