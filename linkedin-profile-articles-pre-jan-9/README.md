# LinkedIn (Profile, Articles) Data

This dataset contains a snapshot of a LinkedIn profile and authored articles exported prior to January 9, 2026.

## Dataset Overview

- **Profile**: Basic identity, headline, and professional summary.
- **Articles**: Full text content, metadata, and links for articles published on the LinkedIn platform.

## Statistics

- **Profile Rows**: 1
- **Articles Authored**: 3
- **Latest Article**: Don't Get Spooked by Ghost Jobs: A Smarter Approach to Your Job Search (2025-04-22)

## Database Schema

The data is stored in a DuckDB database (`data.duckdb`) with the following tables:

### `profile`
User profile information including name, headline, summary, and industry.

### `articles`
LinkedIn articles authored by the user, including title, content, and publication timestamps.

For a detailed column-level schema, see `file 'schema.yaml'`.

## How to Export Your Own Data

1.  Log in to your **LinkedIn** account.
2.  Click on your profile picture (Me) in the top right and select **Settings & Privacy**.
3.  On the left sidebar, click **Data privacy**.
4.  Under the "How LinkedIn uses your data" section, click **Get a copy of your data**.
5.  Select **"Want something in particular? Select the data files you're most interested in"**.
6.  Check **Profile** and **Articles**.
7.  Click **Request archive**.
8.  You will receive an email once your data is ready to download (usually within 24 hours).
9.  Download the zip file and place it in the `source/` directory for ingestion.

## Usage Examples

### View Profile Headline
```sql
SELECT Headline FROM profile;
```

### List Articles by Publication Date
```sql
SELECT title, published_at 
FROM articles 
ORDER BY published_at DESC;
```

### Search Article Content
```sql
SELECT title 
FROM articles 
WHERE content LIKE '%auto-apply%';
```

