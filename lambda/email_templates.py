def get_user_confirmation_email(name, registration_id, amount_paid):
    subject = "A.I. Automation for Non Coders Registration"
    
    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #000000;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        .header {{
            background-color: #000000;
            color: #ffffff;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        .confirmation-box {{
            background-color: #f8f8f8;
            border-left: 4px solid #000000;
            padding: 20px;
            margin: 30px 0;
        }}
        .confirmation-box p {{
            margin: 8px 0;
            font-size: 14px;
        }}
        .confirmation-box .label {{
            color: #666666;
            font-weight: 600;
            display: inline-block;
            width: 120px;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #000000;
        }}
        .info-item {{
            margin: 15px 0;
            padding-left: 25px;
            position: relative;
        }}
        .info-item::before {{
            content: "▪";
            position: absolute;
            left: 0;
            color: #666666;
        }}
        .info-item strong {{
            color: #000000;
        }}
        .video-list {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        .video-list li {{
            margin: 10px 0;
            color: #333333;
        }}
        .video-list a {{
            color: #000000;
            text-decoration: none;
            border-bottom: 1px solid #cccccc;
        }}
        .video-list a:hover {{
            border-bottom-color: #000000;
        }}
        .cta-section {{
            background-color: #f8f8f8;
            padding: 25px;
            text-align: center;
            margin: 30px 0;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            color: #666666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
        .signature {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>A.I. Automation for Non Coders</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Hi {name},</p>
            
            <p>Thank you for registering for <strong>A.I. Automation for Non Coders</strong>!</p>
            
            <p>Your payment has been processed successfully and your registration is confirmed.</p>
            
            <div class="confirmation-box">
                <p><span class="label">Registration ID:</span> <strong>{registration_id}</strong></p>
                <p><span class="label">Amount Paid:</span> <strong>${amount_paid:.2f}</strong></p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Important Information</h2>
                
                <div class="info-item">
                    <strong>Venue Confirmation:</strong> The venue will be confirmed shortly and you'll receive another email with location details.
                </div>
                
                <div class="info-item">
                    <strong>What to Bring:</strong> Please bring your laptop and charger to all sessions.
                </div>
                
                <div class="info-item">
                    <strong>Privacy:</strong> Your email will never be used for anything non-course related.
                </div>
                
                <div class="info-item">
                    <strong>Office Hours:</strong> From 5:30-6:30 PM each night between December 27th and January 4th (except when online courses are scheduled), the instructor will be holding office hours via online chat and will be available to assist you.
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Pre-Course Learning (Optional)</h2>
                <p>If you'd like to get a head start, we recommend watching these videos:</p>
                <ul class="video-list">
                    <li>High-level AI intuition (lighthearted but informative): <a href="https://youtube.com/watch?v=R9OHn5ZF4Uo">Watch Video</a></li>
                    <li>Introduction to n8n: <a href="https://www.youtube.com/watch?v=4cQWJViybAQ&ab_channel=n8n">Watch Video</a></li>
                </ul>
            </div>
            
            <div class="cta-section">
                <p style="margin: 0; color: #333333;">Questions? Please get in touch if you have any issues or questions before the course begins.</p>
            </div>
            
            <div class="signature">
                <p style="margin: 5px 0;">We're excited to have you join us!</p>
                <p style="margin: 5px 0;"><strong>Best regards,</strong></p>
                <p style="margin: 5px 0;">Louka</p>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 A.I. Automation for Non Coders. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
    
    # Plain text fallback for email clients that don't support HTML
    text_body = f"""Hi {name},

Thank you for registering for A.I. Automation for Non Coders!

Your payment has been processed successfully and your registration is confirmed.

Registration ID: {registration_id}
Amount Paid: ${amount_paid:.2f}

IMPORTANT INFORMATION:

▪ Venue Confirmation: The venue will be confirmed shortly and you'll receive another email with location details.

▪ What to Bring: Please bring your laptop and charger to all sessions.

▪ Privacy: Your email will never be used for anything non-course related.

▪ Office Hours: From 5:30-6:30 PM each night between December 27th and January 4th (except when online courses are scheduled), the instructor will be holding office hours via online chat and will be available to assist you.

▪ Pre-Course Learning (Optional): If you'd like to get a head start, we recommend watching these videos:
  • High-level AI intuition (lighthearted but informative): https://youtube.com/watch?v=R9OHn5ZF4Uo
  • Introduction to n8n: https://www.youtube.com/watch?v=4cQWJViybAQ&ab_channel=n8n

Questions: Please get in touch if you have any issues or questions before the course begins.

We're excited to have you join us!

Best regards,
- Louka"""
    
    return subject, html_body, text_body