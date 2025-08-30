#!/usr/bin/env python3

import sys
import os
import webbrowser
import tempfile
from pathlib import Path

# Add the lambda directory to the path so we can import email_templates
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_templates import get_user_confirmation_email

def preview_email(name="John Doe", registration_id="REG-2024-001", amount_paid=299.99):
    """
    Generate and preview the confirmation email in a web browser
    """
    # Get the email content
    subject, html_body, text_body = get_user_confirmation_email(name, registration_id, amount_paid)
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        # Write a complete HTML page with the email preview
        preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Preview: {subject}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}
        .preview-header {{
            background-color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .preview-header h1 {{
            margin: 0 0 10px 0;
            font-size: 20px;
            color: #333333;
        }}
        .preview-info {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            color: #666666;
            font-size: 14px;
        }}
        .preview-info div {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .preview-info strong {{
            color: #000000;
        }}
        .email-container {{
            max-width: 640px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .subject-line {{
            background-color: #f8f8f8;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #000000;
        }}
        .subject-line h2 {{
            margin: 0;
            font-size: 16px;
            color: #333333;
        }}
        .tab-container {{
            margin-bottom: 20px;
        }}
        .tabs {{
            display: flex;
            border-bottom: 2px solid #e0e0e0;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            background-color: #f8f8f8;
            border: none;
            font-size: 14px;
            color: #666666;
            transition: all 0.2s;
        }}
        .tab.active {{
            background-color: #000000;
            color: #ffffff;
        }}
        .tab:hover:not(.active) {{
            background-color: #e0e0e0;
        }}
        .tab-content {{
            display: none;
            padding: 20px 0;
        }}
        .tab-content.active {{
            display: block;
        }}
        .text-content {{
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #333333;
            background-color: #f8f8f8;
            padding: 20px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="preview-header">
        <h1>Email Preview</h1>
        <div class="preview-info">
            <div><strong>To:</strong> {name} (example@email.com)</div>
            <div><strong>Subject:</strong> {subject}</div>
            <div><strong>Registration ID:</strong> {registration_id}</div>
            <div><strong>Amount:</strong> ${amount_paid:.2f}</div>
        </div>
    </div>
    
    <div class="email-container">
        <div class="subject-line">
            <h2>Subject: {subject}</h2>
        </div>
        
        <div class="tab-container">
            <div class="tabs">
                <button class="tab active" onclick="showTab('html')">HTML Version</button>
                <button class="tab" onclick="showTab('text')">Plain Text Version</button>
            </div>
            
            <div id="html-tab" class="tab-content active">
                {html_body}
            </div>
            
            <div id="text-tab" class="tab-content">
                <div class="text-content">{text_body}</div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""
        
        f.write(preview_html)
        temp_file = f.name
    
    # Open the file in the default web browser
    file_url = Path(temp_file).as_uri()
    webbrowser.open(file_url)
    
    print(f"Email preview opened in your browser!")
    print(f"Preview file: {temp_file}")
    print(f"\nPreview Parameters:")
    print(f"  Name: {name}")
    print(f"  Registration ID: {registration_id}")
    print(f"  Amount Paid: ${amount_paid:.2f}")
    print(f"\nYou can customize the preview by passing different parameters:")
    print(f"  python preview_email.py 'Jane Smith' 'REG-2024-002' 199.99")

if __name__ == "__main__":
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        name = sys.argv[1] if len(sys.argv) > 1 else "John Doe"
        registration_id = sys.argv[2] if len(sys.argv) > 2 else "REG-2024-001"
        amount_paid = float(sys.argv[3]) if len(sys.argv) > 3 else 299.99
        preview_email(name, registration_id, amount_paid)
    else:
        # Use default values
        preview_email()