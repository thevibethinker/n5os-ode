#!/usr/bin/env python3
"""
Ingest script for Ben Guo LinkedIn Connections.
Run from dataset root: python ingest/ingest.py

Source: LinkedIn Connections export CSV
Output: data.duckdb with a single 'connections' table
"""
import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.duckdb"
SOURCE_DIR = Path(__file__).parent.parent / "source"


def find_connections_csv() -> Path:
    """Find the LinkedIn connections CSV in source directory."""
    csvs = list(SOURCE_DIR.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV files found in {SOURCE_DIR}")
    if len(csvs) > 1:
        print(f"Warning: Multiple CSVs found, using first: {csvs[0].name}")
    return csvs[0]


def main():
    # Always clean rebuild
    DB_PATH.unlink(missing_ok=True)
    
    csv_path = find_connections_csv()
    print(f"Processing: {csv_path.name}")
    
    con = duckdb.connect(str(DB_PATH))
    
    # LinkedIn exports have a 3-row preamble (notes), actual headers on row 4
    # skip=3 skips the preamble, header=true reads row 4 as column names
    con.execute(f"""
        CREATE TABLE connections AS 
        SELECT 
            "First Name" AS first_name,
            "Last Name" AS last_name,
            "URL" AS linkedin_url,
            "Email Address" AS email,
            "Company" AS company,
            "Position" AS position,
            strptime("Connected On", '%d %b %Y') AS connected_on
        FROM read_csv_auto('{csv_path}', skip=3, header=true)
        WHERE "First Name" IS NOT NULL
        ORDER BY connected_on DESC
    """)
    
    # Add table and column comments
    con.execute("""
        COMMENT ON TABLE connections IS 
        'LinkedIn connections — one row per connection in Ben Guo''s network'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.first_name IS 
        'First name of the connection'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.last_name IS 
        'Last name of the connection (may include credentials like PhD, MBA)'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.linkedin_url IS 
        'Full LinkedIn profile URL'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.email IS 
        'Email address (often NULL — only visible if connection enabled sharing)'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.company IS 
        'Current company/organization listed on profile'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.position IS 
        'Current job title listed on profile'
    """)
    con.execute("""
        COMMENT ON COLUMN connections.connected_on IS 
        'Date the connection was established'
    """)
    
    # Print summary
    count = con.execute("SELECT COUNT(*) FROM connections").fetchone()[0]
    date_range = con.execute("""
        SELECT MIN(connected_on), MAX(connected_on) FROM connections
    """).fetchone()
    
    print(f"Created {DB_PATH}")
    print(f"  connections: {count:,} rows")
    print(f"  Date range: {date_range[0]} to {date_range[1]}")
    
    con.close()


if __name__ == "__main__":
    main()
