import markdown
import pdfkit
import os

def convert_md_to_pdf():
    # Read markdown content
    with open('technical_report.md', 'r') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    # Add CSS for styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 1px solid #eee; }}
            h3 {{ color: #7f8c8d; }}
            code {{ background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }}
            pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f5f6fa; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Save HTML file
    with open('technical_report.html', 'w') as f:
        f.write(styled_html)
    
    # Convert HTML to PDF
    pdfkit.from_file('technical_report.html', 'technical_report.pdf')
    
    # Clean up HTML file
    os.remove('technical_report.html')

if __name__ == '__main__':
    convert_md_to_pdf() 