import os
import csv
import glob
import duckdb
import pandas as pd
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "source", "extracted")
DB_PATH = os.path.join(BASE_DIR, "data.duckdb")

def parse_article(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    title = soup.find('title').get_text(strip=True) if soup.find('title') else ""
    if not title and soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
        
    created_at = ""
    created_tag = soup.find('p', class_='created')
    if created_tag:
        created_at = created_tag.get_text(strip=True).replace("Created on ", "")
        
    published_at = ""
    published_tag = soup.find('p', class_='published')
    if published_tag:
        published_at = published_tag.get_text(strip=True).replace("Published on ", "")
        
    link = ""
    h1_a = soup.select_one('h1 a')
    if h1_a:
        link = h1_a.get('href', "")
        
    image_url = ""
    img_tag = soup.find('img')
    if img_tag:
        image_url = img_tag.get('src', "")
        
    content = ""
    content_div = soup.find('div')
    if content_div:
        content = content_div.get_text(separator="\n", strip=True)
    
    return {
        "title": title,
        "created_at": created_at,
        "published_at": published_at,
        "link": link,
        "image_url": image_url,
        "content": content,
        "file_path": os.path.relpath(file_path, BASE_DIR)
    }

def main():
    print(f"Starting ingestion from {SOURCE_DIR}...")
    con = duckdb.connect(DB_PATH)
    
    # Process Profile
    profile_csv = os.path.join(SOURCE_DIR, "Profile.csv")
    if os.path.exists(profile_csv):
        print("Ingesting profile data...")
        con.execute(f"CREATE OR REPLACE TABLE profile AS SELECT * FROM read_csv_auto('{profile_csv}')")
        
        # Add profile comments
        con.execute("COMMENT ON TABLE profile IS 'User profile information from LinkedIn'")
        con.execute('COMMENT ON COLUMN profile."First Name" IS \'User first name\'')
        con.execute('COMMENT ON COLUMN profile."Last Name" IS \'User last name\'')
        con.execute('COMMENT ON COLUMN profile."Headline" IS \'User professional headline\'')
        con.execute('COMMENT ON COLUMN profile."Summary" IS \'User professional summary\'')
        con.execute('COMMENT ON COLUMN profile."Industry" IS \'Industry the user belongs to\'')
        con.execute('COMMENT ON COLUMN profile."Geo Location" IS \'User geographic location\'')
    
    # Process Articles
    articles_dir = os.path.join(SOURCE_DIR, "Articles", "Articles")
    article_files = glob.glob(os.path.join(articles_dir, "*.html"))
    
    if article_files:
        print(f"Ingesting {len(article_files)} articles...")
        articles_data = [parse_article(f) for f in article_files]
        df_articles = pd.DataFrame(articles_data)
        con.execute("CREATE OR REPLACE TABLE articles AS SELECT * FROM df_articles")
        
        # Add article comments
        con.execute("COMMENT ON TABLE articles IS 'LinkedIn articles authored by the user'")
        con.execute("COMMENT ON COLUMN articles.title IS 'Title of the article'")
        con.execute("COMMENT ON COLUMN articles.created_at IS 'When the article draft was created'")
        con.execute("COMMENT ON COLUMN articles.published_at IS 'When the article was published'")
        con.execute("COMMENT ON COLUMN articles.link IS 'URL link to the article on LinkedIn'")
        con.execute("COMMENT ON COLUMN articles.content IS 'Full text content of the article'")
        con.execute("COMMENT ON COLUMN articles.image_url IS 'URL of the article hero image'")
    
    # Statistics
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    profile_count = con.execute("SELECT COUNT(*) FROM profile").fetchone()[0] if 'profile' in tables else 0
    article_count = con.execute("SELECT COUNT(*) FROM articles").fetchone()[0] if 'articles' in tables else 0
    
    print(f"Ingestion complete. Tables created: profile ({profile_count} rows), articles ({article_count} rows).")
    con.close()

if __name__ == "__main__":
    main()


