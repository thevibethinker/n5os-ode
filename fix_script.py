import sys
from pathlib import Path

script_path = "/home/workspace/N5/scripts/auto_create_stakeholder_profiles.py"
with open(script_path, 'r') as f:
    content = f.read()

# Replace SELECT statement
content = content.replace(
    "cursor.execute('SELECT id, profile_path FROM profiles WHERE email = ?', (email,))",
    "cursor.execute('SELECT id, markdown_path FROM individuals WHERE email = ?', (email,))"
)

# Replace INSERT statement
# INSERT INTO profiles (email, name, organization, profile_path, meeting_date, created_at, enrichment_count)
# individuals: id, full_name, email, linkedin_url, company, title, category, status, priority, tags, first_contact_date, last_contact_date, markdown_path, created_at, updated_at

new_insert = """
        cursor.execute(\"\"\"
            INSERT INTO individuals (email, full_name, company, markdown_path, first_contact_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        \"\"\", (email, name, analysis['organization'], str(profile_rel_path), meeting_date, created_at))
"""

content = content.replace(
    """        cursor.execute(\"\"\"
            INSERT INTO profiles (email, name, organization, profile_path, meeting_date, created_at, enrichment_count)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        \"\"\", (email, name, analysis['organization'], str(profile_rel_path), meeting_date, created_at))""",
    new_insert
)

with open(script_path, 'w') as f:
    f.write(content)

print("Script updated successfully.")
