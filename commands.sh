aws logs tail /aws/lambda/ai-automation-course-registration-handler --since 10m


aws logs tail /aws/lambda/ai-automation-course-payment-webhook


aws logs tail /aws/lambda/ai-automation-course-contact-handler


aws logs tail /aws/lambda/ai-automation-course-livestream-handler




cd tf && terraform output -json > ../test/terraform-outputs.json && terraform output -json > ../src/terraform-outputs.json; cd ../


aws logs tail "/aws/lambda/ai-automation-course-payment-webhook" --since 48h --follow

aws logs tail "/aws/lambda/ai-automation-course-contact-handler" --since 10m --follow


aws lambda list-functions --query 'Functions[*].[FunctionName,Runtime,LastModified]' --output table


ppp  pytest test/integration/test_lambda_health.py -v   

ppp  pytest test/integration/test_contact_form.py -v

aws dynamodb scan --table-name course_registrations --query "Items[*].{Name:name.S, Email:email.S, PaymentStatus:payment_status.S}" --output table  













aws dynamodb scan --table-name course_registrations --projection-expression "course_id,email" --no-cli-pager | jq -r '.Items[] | "aws dynamodb delete-item --table-name course_registrations --key \"{\\\"course_id\\\":{\\\"S\\\":\\\"" 
  + .course_id.S + "\\\"},\\\"email\\\":{\\\"S\\\":\\\"" + .email.S + "\\\"}}\""' | bash


cd tf && terraform apply -auto-approve; cd ../