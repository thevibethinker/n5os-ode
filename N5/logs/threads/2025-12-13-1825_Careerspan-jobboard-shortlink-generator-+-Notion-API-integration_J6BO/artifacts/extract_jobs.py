import re
from bs4 import BeautifulSoup

with open('/home/.z/workspaces/con_BTppAyYnXC0pJ6BO/read_webpage/careerspan.short.gy~~2fjobboard.html', 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Find all job rows (notion-collection-item)
job_rows = soup.select('div.notion-collection-item[data-block-id]')

jobs = []
for row in job_rows:
    block_id = row.get('data-block-id', '')
    
    # Get the name cell (col-index 1)
    name_cell = row.select_one('div[data-col-index="1"] span[style*="font-weight: 500"]')
    title = name_cell.get_text(strip=True) if name_cell else ''
    
    # Get the company cell (col-index 2) 
    company_cell = row.select_one('div[data-col-index="2"] span')
    company = company_cell.get_text(strip=True) if company_cell else ''
    
    # Convert block_id to Notion URL format
    # Format: https://careerspan.notion.site/BLOCKID-WITHOUT-DASHES
    if block_id:
        clean_id = block_id.replace('-', '')
        notion_url = f"https://careerspan.notion.site/{clean_id}"
        
    if title and title != '🛑':  # Skip rows with stop sign
        jobs.append({
            'title': title,
            'company': company,
            'notion_url': notion_url
        })

# Print markdown table
print("| Title | Company | Notion Page Link |")
print("|-------|---------|------------------|")
for job in jobs:
    print(f"| {job['title']} | {job['company']} | [{job['title'][:30]}...]({job['notion_url']}) |")
