#!/usr/bin/env python3
"""LinkedIn full export ingestion.

Run from dataset root:
  python ingest/ingest.py

Contract:
- Always rebuilds ../data.duckdb from scratch
- Reads raw export from ../source (zip) and/or ../source/extracted (files)
- Creates a focused, analysis-ready schema with DuckDB COMMENT metadata
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import duckdb

DATASET_DIR = Path(__file__).resolve().parent.parent
DB_PATH = DATASET_DIR / "data.duckdb"
SOURCE_DIR = DATASET_DIR / "source"
EXTRACTED_DIR = SOURCE_DIR / "extracted"


def _maybe_extract_zip() -> list[Path]:
    """Extract zip exports into source/extracted if needed.

    Returns list of zip paths found.
    """
    zips = sorted(SOURCE_DIR.glob("*.zip"))
    if not zips:
        return []

    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    # If extracted already has files, do not re-extract automatically (avoid churn)
    existing_files = [p for p in EXTRACTED_DIR.rglob("*") if p.is_file()]
    if existing_files:
        return zips

    for zp in zips:
        with zipfile.ZipFile(zp, "r") as zf:
            zf.extractall(EXTRACTED_DIR)

    return zips


def _table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    return (
        con.execute(
            "SELECT COUNT(*) FROM duckdb_tables() WHERE schema_name='main' AND table_name = ?",
            [table_name],
        ).fetchone()[0]
        > 0
    )


def main() -> None:
    DB_PATH.unlink(missing_ok=True)

    zips = _maybe_extract_zip()

    if not EXTRACTED_DIR.exists() or not any(p.is_file() for p in EXTRACTED_DIR.rglob("*")):
        raise SystemExit(
            "No extracted source files found. Put your LinkedIn export zip in source/ "
            "(or extracted files in source/extracted/) and re-run."
        )

    con = duckdb.connect(str(DB_PATH))

    # Extensions (none required); keep deterministic settings.
    con.execute("PRAGMA enable_progress_bar=false")

    def csv_path(rel: str) -> str:
        return str((EXTRACTED_DIR / rel).as_posix())

    # --- Core tables (focused scope) ---

    # Profile
    con.execute(
        """
        CREATE TABLE profile AS
        SELECT
          "First Name"::VARCHAR AS first_name,
          "Last Name"::VARCHAR AS last_name,
          "Maiden Name"::VARCHAR AS maiden_name,
          "Address"::VARCHAR AS address,
          "Birth Date"::VARCHAR AS birth_date_raw,
          "Headline"::VARCHAR AS headline,
          "Summary"::VARCHAR AS summary,
          "Industry"::VARCHAR AS industry,
          TRY_CAST("Zip Code" AS INTEGER) AS zip_code,
          "Geo Location"::VARCHAR AS geo_location,
          "Twitter Handles"::VARCHAR AS twitter_handles,
          "Websites"::VARCHAR AS websites,
          "Instant Messengers"::VARCHAR AS instant_messengers
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Profile.csv")],
    )

    # Positions
    con.execute(
        """
        CREATE TABLE positions AS
        SELECT
          "Company Name"::VARCHAR AS company_name,
          "Title"::VARCHAR AS title,
          "Description"::VARCHAR AS description,
          "Location"::VARCHAR AS location,
          TRY_STRPTIME(NULLIF("Started On", ''), '%b %Y')::DATE AS started_on,
          TRY_STRPTIME(NULLIF("Finished On", ''), '%b %Y')::DATE AS finished_on,
          "Started On"::VARCHAR AS started_on_raw,
          "Finished On"::VARCHAR AS finished_on_raw
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Positions.csv")],
    )

    # Education
    con.execute(
        """
        CREATE TABLE education AS
        SELECT
          "School Name"::VARCHAR AS school_name,
          TRY_CAST(NULLIF(CAST("Start Date" AS VARCHAR), '') AS INTEGER) AS start_year,
          TRY_CAST(NULLIF(CAST("End Date" AS VARCHAR), '') AS INTEGER) AS end_year,
          "Degree Name"::VARCHAR AS degree_name,
          "Activities"::VARCHAR AS activities,
          "Notes"::VARCHAR AS notes
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Education.csv")],
    )

    # Skills
    con.execute(
        """
        CREATE TABLE skills AS
        SELECT
          "Name"::VARCHAR AS skill_name
        FROM read_csv_auto(?, header=true)
        WHERE NULLIF("Name", '') IS NOT NULL
        """,
        [csv_path("Skills.csv")],
    )

    # Connections
    con.execute(
        """
        CREATE TABLE connections AS
        SELECT
          "First Name"::VARCHAR AS first_name,
          "Last Name"::VARCHAR AS last_name,
          "URL"::VARCHAR AS profile_url,
          "Email Address"::VARCHAR AS email_address,
          "Company"::VARCHAR AS company,
          "Position"::VARCHAR AS position,
          TRY_STRPTIME(NULLIF("Connected On", ''), '%d %b %Y')::DATE AS connected_on,
          "Connected On"::VARCHAR AS connected_on_raw
        FROM read_csv_auto(?, header=true, skip=3)
        """,
        [csv_path("Connections.csv")],
    )

    # Messages
    con.execute(
        """
        CREATE TABLE messages AS
        SELECT
          "CONVERSATION ID"::VARCHAR AS conversation_id,
          "CONVERSATION TITLE"::VARCHAR AS conversation_title,
          "FROM"::VARCHAR AS sender_name,
          "SENDER PROFILE URL"::VARCHAR AS sender_profile_url,
          "TO"::VARCHAR AS recipient_names,
          "RECIPIENT PROFILE URLS"::VARCHAR AS recipient_profile_urls,
          TRY_STRPTIME(REPLACE(NULLIF(CAST("DATE" AS VARCHAR), ''), ' UTC', ''), '%Y-%m-%d %H:%M:%S') AS sent_at,
          CAST("DATE" AS VARCHAR) AS sent_at_raw,
          "SUBJECT"::VARCHAR AS subject,
          "CONTENT"::VARCHAR AS content,
          "FOLDER"::VARCHAR AS folder,
          "ATTACHMENTS"::VARCHAR AS attachments,
          ("FROM" = 'Vrijen Attawar') AS is_from_v
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("messages.csv")],
    )

    # Shares (posts)
    con.execute(
        """
        CREATE TABLE shares AS
        SELECT
          TRY_STRPTIME(NULLIF(CAST("Date" AS VARCHAR), ''), '%Y-%m-%d %H:%M:%S') AS shared_at,
          CAST("Date" AS VARCHAR) AS shared_at_raw,
          "ShareLink"::VARCHAR AS share_link,
          "ShareCommentary"::VARCHAR AS share_commentary,
          "SharedUrl"::VARCHAR AS shared_url,
          "MediaUrl"::VARCHAR AS media_url,
          "Visibility"::VARCHAR AS visibility
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Shares.csv")],
    )

    # Comments
    con.execute(
        """
        CREATE TABLE comments AS
        SELECT
          TRY_STRPTIME(NULLIF(CAST("Date" AS VARCHAR), ''), '%Y-%m-%d %H:%M:%S') AS commented_at,
          CAST("Date" AS VARCHAR) AS commented_at_raw,
          "Link"::VARCHAR AS link,
          "Message"::VARCHAR AS message
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Comments.csv")],
    )

    # Reactions
    con.execute(
        """
        CREATE TABLE reactions AS
        SELECT
          TRY_STRPTIME(NULLIF(CAST("Date" AS VARCHAR), ''), '%Y-%m-%d %H:%M:%S') AS reacted_at,
          CAST("Date" AS VARCHAR) AS reacted_at_raw,
          "Type"::VARCHAR AS reaction_type,
          "Link"::VARCHAR AS link
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Reactions.csv")],
    )

    # Search queries
    con.execute(
        """
        CREATE TABLE search_queries AS
        SELECT
          CAST("Time" AS TIMESTAMP) AS searched_at,
          CAST("Time" AS VARCHAR) AS searched_at_raw,
          "Search Query"::VARCHAR AS search_query
        FROM read_csv(?, header=true, delim=',', strict_mode=false, ignore_errors=true)
        """,
        [csv_path("SearchQueries.csv")],
    )

    # Invitations
    con.execute(
        """
        CREATE TABLE invitations AS
        SELECT
          "From"::VARCHAR AS from_name,
          "To"::VARCHAR AS to_name,
          TRY_STRPTIME(NULLIF("Sent At", ''), '%m/%d/%y, %I:%M %p') AS sent_at,
          "Sent At"::VARCHAR AS sent_at_raw,
          "Message"::VARCHAR AS message,
          "Direction"::VARCHAR AS direction,
          "inviterProfileUrl"::VARCHAR AS inviter_profile_url,
          "inviteeProfileUrl"::VARCHAR AS invitee_profile_url
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Invitations.csv")],
    )

    # Job applications
    con.execute(
        """
        CREATE TABLE job_applications AS
        SELECT
          TRY_STRPTIME(NULLIF("Application Date", ''), '%m/%d/%y, %I:%M %p') AS applied_at,
          "Application Date"::VARCHAR AS applied_at_raw,
          "Contact Email"::VARCHAR AS contact_email,
          "Contact Phone Number"::VARCHAR AS contact_phone_number,
          "Company Name"::VARCHAR AS company_name,
          "Job Title"::VARCHAR AS job_title,
          "Job Url"::VARCHAR AS job_url,
          "Resume Name"::VARCHAR AS resume_name,
          "Question And Answers"::VARCHAR AS question_and_answers
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Jobs/Job Applications.csv")],
    )

    # Learning history
    con.execute(
        """
        CREATE TABLE learning AS
        SELECT
          "Content Title"::VARCHAR AS content_title,
          "Content Description"::VARCHAR AS content_description,
          "Content Type"::VARCHAR AS content_type,
          TRY_STRPTIME(REPLACE(NULLIF(CAST("Content Last Watched Date (if viewed)" AS VARCHAR), ''), ' UTC', ''), '%Y-%m-%d %H:%M') AS last_watched_at,
          CAST("Content Last Watched Date (if viewed)" AS VARCHAR) AS last_watched_at_raw,
          TRY_STRPTIME(REPLACE(NULLIF(CAST("Content Completed At (if completed)" AS VARCHAR), ''), ' UTC', ''), '%Y-%m-%d %H:%M') AS completed_at,
          CAST("Content Completed At (if completed)" AS VARCHAR) AS completed_at_raw,
          TRY_CAST(NULLIF(CAST("Content Saved" AS VARCHAR), '') AS BOOLEAN) AS content_saved,
          "Notes taken on videos (if taken)"::VARCHAR AS video_notes,
          "column7"::VARCHAR AS notes
        FROM read_csv_auto(?, header=true)
        """,
        [csv_path("Learning.csv")],
    )

    # --- Comments (DuckDB metadata) ---

    con.execute("COMMENT ON TABLE profile IS 'Your LinkedIn profile export (single row) with headline/summary and basic account info'"
    )
    con.execute("COMMENT ON COLUMN profile.first_name IS 'First name on LinkedIn profile'")
    con.execute("COMMENT ON COLUMN profile.last_name IS 'Last name on LinkedIn profile'")
    con.execute("COMMENT ON COLUMN profile.maiden_name IS 'Maiden name (if present)'")
    con.execute("COMMENT ON COLUMN profile.address IS 'Profile address/location string from export'")
    con.execute("COMMENT ON COLUMN profile.birth_date_raw IS 'Birth date field as exported (often month/day, may omit year)'")
    con.execute("COMMENT ON COLUMN profile.headline IS 'LinkedIn headline'")
    con.execute("COMMENT ON COLUMN profile.summary IS 'LinkedIn About/Summary text'")
    con.execute("COMMENT ON COLUMN profile.industry IS 'Industry label on profile'")
    con.execute("COMMENT ON COLUMN profile.zip_code IS 'Zip code from profile (if provided)'")
    con.execute("COMMENT ON COLUMN profile.geo_location IS 'LinkedIn geo location / metro area'")
    con.execute("COMMENT ON COLUMN profile.twitter_handles IS 'Twitter/X handles field from export'")
    con.execute("COMMENT ON COLUMN profile.websites IS 'Websites field from export'")
    con.execute("COMMENT ON COLUMN profile.instant_messengers IS 'Instant messenger handles field from export'")

    con.execute("COMMENT ON TABLE positions IS 'Work experience entries from your LinkedIn profile (one row per position)'")
    con.execute("COMMENT ON COLUMN positions.company_name IS 'Company or organization name'")
    con.execute("COMMENT ON COLUMN positions.title IS 'Role title'")
    con.execute("COMMENT ON COLUMN positions.description IS 'Role description text'")
    con.execute("COMMENT ON COLUMN positions.location IS 'Location string for the position'")
    con.execute("COMMENT ON COLUMN positions.started_on IS 'Parsed start month (stored as DATE, first day of month)'")
    con.execute("COMMENT ON COLUMN positions.finished_on IS 'Parsed end month (stored as DATE, first day of month); NULL means ongoing'")
    con.execute("COMMENT ON COLUMN positions.started_on_raw IS 'Start date string as exported'")
    con.execute("COMMENT ON COLUMN positions.finished_on_raw IS 'End date string as exported'")

    con.execute("COMMENT ON TABLE education IS 'Education entries from your LinkedIn profile (one row per school/program)'")
    con.execute("COMMENT ON COLUMN education.school_name IS 'School name'")
    con.execute("COMMENT ON COLUMN education.start_year IS 'Start year (integer)'")
    con.execute("COMMENT ON COLUMN education.end_year IS 'End year (integer)'")
    con.execute("COMMENT ON COLUMN education.degree_name IS 'Degree name (as exported)'")
    con.execute("COMMENT ON COLUMN education.activities IS 'Activities/clubs field'")
    con.execute("COMMENT ON COLUMN education.notes IS 'Notes field from export (often course lists)'")

    con.execute("COMMENT ON TABLE skills IS 'Skills listed on your LinkedIn profile (one row per skill)'")
    con.execute("COMMENT ON COLUMN skills.skill_name IS 'Skill name'")

    con.execute("COMMENT ON TABLE connections IS 'LinkedIn connections (one row per connection)'")
    con.execute("COMMENT ON COLUMN connections.first_name IS 'Connection first name'")
    con.execute("COMMENT ON COLUMN connections.last_name IS 'Connection last name'")
    con.execute("COMMENT ON COLUMN connections.profile_url IS 'Connection LinkedIn profile URL'")
    con.execute("COMMENT ON COLUMN connections.email_address IS 'Email address if the connection allows sharing (often blank)'")
    con.execute("COMMENT ON COLUMN connections.company IS 'Company name as exported at time of export'")
    con.execute("COMMENT ON COLUMN connections.position IS 'Job title as exported at time of export'")
    con.execute("COMMENT ON COLUMN connections.connected_on IS 'Date you connected (parsed)'")
    con.execute("COMMENT ON COLUMN connections.connected_on_raw IS 'Connected On field as exported'")

    con.execute("COMMENT ON TABLE messages IS 'LinkedIn messages export (one row per message)'")
    con.execute("COMMENT ON COLUMN messages.conversation_id IS 'LinkedIn conversation identifier'")
    con.execute("COMMENT ON COLUMN messages.conversation_title IS 'Conversation title if present (often blank)'")
    con.execute("COMMENT ON COLUMN messages.sender_name IS 'Sender display name'")
    con.execute("COMMENT ON COLUMN messages.sender_profile_url IS 'Sender LinkedIn profile URL'")
    con.execute("COMMENT ON COLUMN messages.recipient_names IS 'Recipient display names (comma-separated)'")
    con.execute("COMMENT ON COLUMN messages.recipient_profile_urls IS 'Recipient profile URLs (comma-separated, aligns to recipient_names)'")
    con.execute("COMMENT ON COLUMN messages.sent_at IS 'Timestamp parsed from exported DATE field (UTC)'")
    con.execute("COMMENT ON COLUMN messages.sent_at_raw IS 'DATE field as exported (string)'")
    con.execute("COMMENT ON COLUMN messages.subject IS 'Message subject (often blank)'")
    con.execute("COMMENT ON COLUMN messages.content IS 'Message body text'")
    con.execute("COMMENT ON COLUMN messages.folder IS 'Mailbox folder (e.g., INBOX)'")
    con.execute("COMMENT ON COLUMN messages.attachments IS 'Attachment field as exported'")
    con.execute("COMMENT ON COLUMN messages.is_from_v IS 'True if sender_name equals Vrijen Attawar'")

    con.execute("COMMENT ON TABLE shares IS 'Your LinkedIn shares/posts export (one row per share)'")
    con.execute("COMMENT ON COLUMN shares.shared_at IS 'When the share/post was created (parsed)'")
    con.execute("COMMENT ON COLUMN shares.shared_at_raw IS 'Date field as exported'")
    con.execute("COMMENT ON COLUMN shares.share_link IS 'Link to the share/post'")
    con.execute("COMMENT ON COLUMN shares.share_commentary IS 'Post text/commentary'")
    con.execute("COMMENT ON COLUMN shares.shared_url IS 'URL shared (if post shared a URL)'")
    con.execute("COMMENT ON COLUMN shares.media_url IS 'Media URL (if present)'")
    con.execute("COMMENT ON COLUMN shares.visibility IS 'Visibility setting as exported'")

    con.execute("COMMENT ON TABLE comments IS 'Your LinkedIn comments export (one row per comment)'")
    con.execute("COMMENT ON COLUMN comments.commented_at IS 'When the comment was created (parsed)'")
    con.execute("COMMENT ON COLUMN comments.commented_at_raw IS 'Date field as exported'")
    con.execute("COMMENT ON COLUMN comments.link IS 'Link to the activity/comment thread'")
    con.execute("COMMENT ON COLUMN comments.message IS 'Comment text'")

    con.execute("COMMENT ON TABLE reactions IS 'Your LinkedIn reactions (likes, empathy, etc.) export (one row per reaction)'")
    con.execute("COMMENT ON COLUMN reactions.reacted_at IS 'When the reaction was recorded (parsed)'")
    con.execute("COMMENT ON COLUMN reactions.reacted_at_raw IS 'Date field as exported'")
    con.execute("COMMENT ON COLUMN reactions.reaction_type IS 'Reaction type (e.g., LIKE, EMPATHY)'")
    con.execute("COMMENT ON COLUMN reactions.link IS 'Link to the reacted-to activity'")

    con.execute("COMMENT ON TABLE search_queries IS 'LinkedIn search queries you performed (one row per search)'")
    con.execute("COMMENT ON COLUMN search_queries.searched_at IS 'When the search occurred (parsed, UTC)'")
    con.execute("COMMENT ON COLUMN search_queries.searched_at_raw IS 'Time field as exported'")
    con.execute("COMMENT ON COLUMN search_queries.search_query IS 'Search query string'")

    con.execute("COMMENT ON TABLE invitations IS 'Connection invitations sent/received (one row per invite)'")
    con.execute("COMMENT ON COLUMN invitations.from_name IS 'Inviter name'")
    con.execute("COMMENT ON COLUMN invitations.to_name IS 'Invitee name'")
    con.execute("COMMENT ON COLUMN invitations.sent_at IS 'When invite was sent (parsed; timezone not included in export)'")
    con.execute("COMMENT ON COLUMN invitations.sent_at_raw IS 'Sent At field as exported'")
    con.execute("COMMENT ON COLUMN invitations.message IS 'Invitation message text (if provided)'")
    con.execute("COMMENT ON COLUMN invitations.direction IS 'OUTGOING or INCOMING as exported'")
    con.execute("COMMENT ON COLUMN invitations.inviter_profile_url IS 'Inviter LinkedIn profile URL'")
    con.execute("COMMENT ON COLUMN invitations.invitee_profile_url IS 'Invitee LinkedIn profile URL'")

    con.execute("COMMENT ON TABLE job_applications IS 'Jobs you applied to via LinkedIn Easy Apply / job applications export (one row per application)'")
    con.execute("COMMENT ON COLUMN job_applications.applied_at IS 'Application timestamp parsed from export'")
    con.execute("COMMENT ON COLUMN job_applications.applied_at_raw IS 'Application Date field as exported'")
    con.execute("COMMENT ON COLUMN job_applications.contact_email IS 'Email used for the application (often your email)'")
    con.execute("COMMENT ON COLUMN job_applications.contact_phone_number IS 'Phone number used for the application'")
    con.execute("COMMENT ON COLUMN job_applications.company_name IS 'Company name'")
    con.execute("COMMENT ON COLUMN job_applications.job_title IS 'Job title'")
    con.execute("COMMENT ON COLUMN job_applications.job_url IS 'Job posting URL'")
    con.execute("COMMENT ON COLUMN job_applications.resume_name IS 'Resume filename used'")
    con.execute("COMMENT ON COLUMN job_applications.question_and_answers IS 'Raw Q&A blob from Easy Apply (may contain HTML)'")

    con.execute("COMMENT ON TABLE learning IS 'LinkedIn Learning activity (one row per content item)'")
    con.execute("COMMENT ON COLUMN learning.content_title IS 'Content title'")
    con.execute("COMMENT ON COLUMN learning.content_description IS 'Content description (may contain HTML)'")
    con.execute("COMMENT ON COLUMN learning.content_type IS 'Content type (e.g., Course)'")
    con.execute("COMMENT ON COLUMN learning.last_watched_at IS 'Last watched timestamp parsed from export (UTC removed; stored as TIMESTAMP)'")
    con.execute("COMMENT ON COLUMN learning.last_watched_at_raw IS 'Last watched field as exported'")
    con.execute("COMMENT ON COLUMN learning.completed_at IS 'Completion timestamp parsed from export (UTC removed; stored as TIMESTAMP)'")
    con.execute("COMMENT ON COLUMN learning.completed_at_raw IS 'Completion field as exported'")
    con.execute("COMMENT ON COLUMN learning.content_saved IS 'Whether the item was saved (boolean)'")
    con.execute("COMMENT ON COLUMN learning.video_notes IS 'Notes taken on videos field from export'")
    con.execute("COMMENT ON COLUMN learning.notes IS 'Notes field from export'")

    # Lightweight sanity checks
    for t in [
        "profile",
        "positions",
        "education",
        "skills",
        "connections",
        "messages",
        "shares",
        "comments",
        "reactions",
        "search_queries",
        "invitations",
        "job_applications",
        "learning",
    ]:
        if not _table_exists(con, t):
            raise RuntimeError(f"Expected table missing: {t}")

    con.close()

    zip_note = f" (source zip(s): {len(zips)})" if zips else ""
    print(f"Created {DB_PATH}{zip_note}")


if __name__ == "__main__":
    main()








