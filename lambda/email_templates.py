def get_user_confirmation_email(name, registration_id, amount_paid):
    subject = "A.I. Automation for Non Coders Registration"
    
    body = f"""Hi {name},

Thank you for registering for A.I. Automation for Non Coders!

Your payment has been processed successfully and your registration is confirmed.

Registration ID: {registration_id}
Amount Paid: ${amount_paid:.2f}

IMPORTANT INFORMATION:

🏢 Venue Confirmation: The venue will be confirmed shortly and you'll receive another email with location details.

💻 What to Bring: Please bring your laptop and charger to all sessions.

📧 Privacy: Your email will never be used for anything non-course related.

🕰️ Office Hours: From 5:30-6:30 PM each night between December 27th and January 4th (except when online courses are scheduled), the instructor will be holding office hours via online chat and will be available to assist you.

📚 Pre-Course Learning (Optional): If you'd like to get a head start, we recommend watching these videos:
• High-level AI intuition (lighthearted but informative): https://youtube.com/watch?v=R9OHn5ZF4Uo
• Introduction to n8n: https://www.youtube.com/watch?v=4cQWJViybAQ&ab_channel=n8n

❓ Questions: Please get in touch if you have any issues or questions before the course begins.

We're excited to have you join us!

Best regards,
- Louka"""
    
    return subject, body