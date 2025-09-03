#!/usr/bin/env python3
"""
Convert HTML file to PDF using weasyprint.
Usage: python html_to_pdf.py
"""

import os
import sys
from pathlib import Path

def install_weasyprint():
    """Install weasyprint if not available."""
    try:
        import weasyprint
        return True
    except ImportError:
        print("weasyprint not found. Installing...")
        os.system("pip install weasyprint")
        try:
            import weasyprint
            return True
        except ImportError:
            print("Failed to install weasyprint. Please install manually: pip install weasyprint")
            return False

def convert_html_to_pdf(html_file_path, output_pdf_path=None):
    """Convert HTML file to PDF."""
    if not install_weasyprint():
        return False
    
    import weasyprint
    
    # Set default output path if not provided
    if output_pdf_path is None:
        html_path = Path(html_file_path)
        output_pdf_path = html_path.with_suffix('.pdf')
    
    try:
        # Read HTML file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to PDF
        html_doc = weasyprint.HTML(string=html_content, base_url=str(Path(html_file_path).parent))
        html_doc.write_pdf(output_pdf_path)
        
        print(f"Successfully converted {html_file_path} to {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        return False

def main():
    # Convert the specific file
    html_file = "/Users/plato/code/course/course-design/automation-course-onepager.html"
    
    if not os.path.exists(html_file):
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    success = convert_html_to_pdf(html_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()