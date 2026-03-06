import os
import re

def markdown_to_html(md_file, html_file):
    if not os.path.exists(md_file):
        print(f"[ERROR] Markdown file {md_file} not found.")
        return
        
    with open(md_file, 'r') as f:
        md_content = f.read()

    # Very basic and robust markdown parsing into HTML
    html_content = md_content
    
    # Headers
    html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    
    # Bold text
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Links
    html_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" class="apply-btn">\1</a>', html_content)
    
    # Lists (ul/li for single dash items)
    html_content = re.sub(r'^- (.*?)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    
    # Wrap elements in paragraphs where needed (simple approach: split by double newline)
    blocks = html_content.split('\n\n')
    formatted_blocks = []
    
    in_list = False
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        if block.startswith('<h'):
            formatted_blocks.append(block)
        elif block.startswith('<li>'):
            # Wrap contiguous li's in ul
            block = f'<ul>\n{block}\n</ul>'
            formatted_blocks.append(block)
        else:
            formatted_blocks.append(f'<p>{block}</p>')
            
    html_body = '\n'.join(formatted_blocks)
    
    # Full HTML wrapper with styling
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Hunter Daily Report</title>
    <style>
        :root {{
            --primary: #2563eb;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--background);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 2rem 1rem;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: var(--primary);
        }}
        
        h2 {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
            margin-top: 2rem;
        }}
        
        h3 {{
            color: var(--primary);
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        
        ul {{
            list-style: none;
            padding: 0;
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            margin-bottom: 2rem;
        }}
        
        li {{
            margin-bottom: 0.75rem;
        }}
        
        li strong {{
            color: #334155;
        }}
        
        .apply-btn {{
            display: inline-block;
            background-color: var(--primary);
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            margin-top: 1rem;
            transition: background-color 0.2s;
        }}
        
        .apply-btn:hover {{
            background-color: #1d4ed8;
        }}
        
        p {{
            margin-bottom: 1rem;
        }}
        
        strong {{
            font-weight: 600;
        }}

        .update-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--card-bg);
            border-top: 1px solid #e2e8f0;
            padding: 0.75rem 1rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 -2px 8px rgb(0 0 0 / 0.08);
            z-index: 100;
        }}

        .update-bar span {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}

        .update-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background-color: #059669;
            color: white;
            padding: 0.5rem 1.2rem;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.9rem;
            transition: background-color 0.2s;
        }}

        .update-btn:hover {{
            background-color: #047857;
        }}

        .container {{
            padding-bottom: 4rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
    <div class="update-bar">
        <span>Data not fresh?</span>
        <a href="https://github.com/Bluntboy101/job-hunter-site/actions/workflows/daily-update.yml" target="_blank" class="update-btn">
            &#x21bb; Update Now
        </a>
    </div>
</body>
</html>"""

    output_dir = os.path.dirname(html_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(html_file, 'w') as f:
        f.write(full_html)
        
    print(f"[SUCCESS] HTML report published to: {html_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert markdown report to HTML.")
    parser.add_argument("--input", type=str, default="deliverables/job_report.md", help="Input markdown file")
    parser.add_argument("--output", type=str, default="deliverables/job_report.html", help="Output HTML file")
    args = parser.parse_args()
    markdown_to_html(args.input, args.output)
