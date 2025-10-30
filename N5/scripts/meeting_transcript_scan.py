import json
import os
import re
from datetime import datetime
from pathlib import Path
import asyncio

# --- Configuration ---
GOOGLE_DRIVE_TRANSCRIPT_FOLDER_ID = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"
INBOX_PATH = Path("/home/workspace/N5/inbox/meeting_requests")
PROCESSED_PATH = Path("/home/workspace/N5/inbox/meeting_requests/processed")
COMPLETED_PATH = Path("/home/workspace/N5/inbox/meeting_requests/completed")
RECORDS_PATH = Path("/home/workspace/Personal/Meetings")
TRANSCRIPTS_INBOX = Path("/home/workspace/N5/inbox/transcripts")

# Ensure directories exist
INBOX_PATH.mkdir(parents=True, exist_ok=True)
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
COMPLETED_PATH.mkdir(parents=True, exist_ok=True)
TRANSCRIPTS_INBOX.mkdir(parents=True, exist_ok=True)

# --- Helper Functions ---

def load_gdrive_ids_from_json_files(directory: Path) -> set:
    """Loads gdrive_ids from all JSON files in the specified directory and its subdirectories."""
    ids = set()
    if not directory.exists():
        return ids
    for file_path in directory.rglob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'gdrive_id' in data:
                    ids.add(data['gdrive_id'])
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return ids

def load_gdrive_ids_from_metadata_files(directory: Path) -> set:
    """Loads gdrive_ids from all _metadata.json files in specified directory and its subdirectories."""
    ids = set()
    if not directory.exists():
        return ids
    for file_path in directory.rglob("_metadata.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'gdrive_id' in data:
                    ids.add(data['gdrive_id'])
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return ids

def extract_date_from_filename(filename: str) -> str:
    """Extracts date (YYYY-MM-DD) from various filename formats."""
    match = re.search(r'\\d{4}-\\d{2}-\\d{2}', filename)
    if match:
        return match.group(0)
    # Fallback for filenames like "Oct 25" - not ideal, but better than nothing
    try:
        month_day_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s(\\d{1,2})', filename)
        if month_day_match:
            month_name = month_day_match.group(1)
            day = int(month_day_match.group(2))
            month_num = datetime.strptime(month_name, '%b').month
            current_year = datetime.now().year # Assume current year if not present
            return f"{current_year:04d}-{month_num:02d}-{day:02d}"
    except:
        pass
    return datetime.now().strftime("%Y-%m-%d") # Default to today if no date found

def extract_time_from_filename(filename: str) -> str:
    """Extracts time (HHMMSS) from filename, or returns empty string."""
    match = re.search(r'(\\d{2})(\\d{2})(\\d{2})_transcript', filename) # e.g., 164313_transcript
    if match:
        return f"{match.group(1)}{match.group(2)}{match.group(3)}"
    return ""

def classify_meeting_and_extract_participant(filename: str, transcript_content: str) -> tuple[str, str]:
    """Classifies meeting as internal/external and extracts participant slug for external meetings."""
    internal_keywords = ["daily team stand-up", "co-founder", "extended cof", "bi-weekly extended"]
    external_domains = ["@mycareerspan.com", "@theapply.ai"]

    is_internal = False
    for keyword in internal_keywords:
        if keyword in filename.lower():
            is_internal = True
            break
    
    if not is_internal:
        # Check transcript content for internal domains if not classified by filename
        for domain in external_domains:
            if domain in transcript_content:
                is_internal = True
                break

    if is_internal:
        return "internal", "internal-team"
    else:
        # Extract external participant
        # Look for patterns like "Name x Vrijen" or "Name - Org"
        participant_match = re.search(r'(.*?)(?: - | x Vrijen| and Vrijen Attawar| \\+ Logan Currie)?(?: -transcript-)?(?:\\.docx|\\.txt)?$', filename, re.IGNORECASE)
        participant_name = filename.replace("-transcript", "").replace(".docx", "").replace(".txt", "")

        if participant_match and participant_match.group(1):
             participant_name = participant_match.group(1).strip()
             # Clean up common phrases
             participant_name = re.sub(r'(x Vrijen|and Vrijen Attawar|\\+ Logan Currie)', '', participant_name, flags=re.IGNORECASE).strip()
             participant_name = re.sub(r'[^a-zA-Z0-9\\s-]', '', participant_name).strip() # Remove special chars
             participant_name = re.sub(r'\\s+', '-', participant_name).lower() # Slugify spaces

        if not participant_name:
            participant_name = "unknown"
        
        return "external", participant_name

def generate_meeting_id(date: str, classification: str, participant_slug: str, existing_ids: set) -> str:
    """Generates a unique meeting ID, appending time if necessary."""
    base_id = f"{date}_{classification}-{participant_slug}"
    meeting_id = base_id
    counter = 1
    while meeting_id in existing_ids: # This logic needs access to all existing meeting IDs
        # Append time or increment counter
        if not re.search(r'\_\\d{6}$', meeting_id): # Check if time already appended
            meeting_id = f"{base_id}_{datetime.now().strftime('%H%M%S')}"
        else:
            meeting_id = f"{base_id}_{datetime.now().strftime('%H%M%S')}_{counter}"
            counter += 1
    return meeting_id

# --- Mock Google Drive API calls for demonstration ---
async def mock_google_drive_list_files(folder_id: str) -> dict:
    print(f"MOCK: Listing files from Google Drive folder ID: {folder_id}...")
    # Sample data for demonstration
    return {
        "files": [
            {
                "id": "mock_gdrive_id_1",
                "name": "2025-10-25_internal-daily-standup-transcript.docx",
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "modifiedTime": "2025-10-25T10:00:00Z",
                "webViewLink": "https://docs.google.com/document/d/mock_gdrive_id_1"
            },
            {
                "id": "mock_gdrive_id_2",
                "name": "Alex x Vrijen - Wisdom Partners Coaching - 2025-10-24-transcript.txt",
                "mimeType": "text/plain",
                "modifiedTime": "2025-10-24T15:30:00Z",
                "webViewLink": "https://docs.google.com/document/d/mock_gdrive_id_2"
            },
            {
                "id": "mock_gdrive_id_3_processed",
                "name": "[ZO-PROCESSED] Old Meeting Transcript.txt",
                "mimeType": "text/plain",
                "modifiedTime": "2025-10-20T11:00:00Z",
                "webViewLink": "https://docs.google.com/document/d/mock_gdrive_id_3_processed"
            },
            {
                "id": "mock_gdrive_id_4",
                "name": "2025-10-25_external-new-client-pitch-transcript.txt",
                "mimeType": "text/plain",
                "modifiedTime": "2025-10-25T11:45:00Z",
                "webViewLink": "https://docs.google.com/document/d/mock_gdrive_id_4"
            },
            {
                "id": "mock_gdrive_id_5_duplicate",
                "name": "Duplicate Existing Meeting.txt",
                "mimeType": "text/plain",
                "modifiedTime": "2025-10-23T09:00:00Z",
                "webViewLink": "https://docs.google.com/document/d/mock_gdrive_id_5_duplicate"
            }
        ]
    }

async def mock_google_drive_download_file(file_id: str, file_path: str) -> dict:
    print(f"MOCK: Downloading file {file_id} to {file_path}...")
    # Simulate writing content to the file
    content = f"This is a mock transcript content for {file_id}.\n"
    if file_id == "mock_gdrive_id_1":
        content += "Internal keywords like co-founder and daily team stand-up are present."
    elif file_id == "mock_gdrive_id_2":
        content += "External participant is Alex from Wisdom Partners. No internal domains here."
    elif file_id == "mock_gdrive_id_4":
        content += "This is an external new client pitch. Careerspan mentioned."

    with open(file_path, "w") as f:
        f.write(content)
    return {"filePath": file_path}


async def main():
    print("Starting meeting transcript scan...")

    # 1. Load Existing gdrive_ids for deduplication
    print("Loading existing gdrive_ids...")
    existing_gdrive_ids = set()
    existing_gdrive_ids.add("mock_gdrive_id_5_duplicate") # Add a dummy ID to test deduplication
    existing_gdrive_ids.update(load_gdrive_ids_from_json_files(INBOX_PATH))
    existing_gdrive_ids.update(load_gdrive_ids_from_json_files(PROCESSED_PATH))
    existing_gdrive_ids.update(load_gdrive_ids_from_json_files(COMPLETED_PATH))
    existing_gdrive_ids.update(load_gdrive_ids_from_metadata_files(RECORDS_PATH))
    print(f"Loaded {len(existing_gdrive_ids)} existing gdrive_ids (including mock duplicates).")

    # Get a list of existing meeting IDs (filenames of request files)
    existing_meeting_ids = set([f.stem.replace('_request', '') for f in INBOX_PATH.rglob('*_request.json')])
    existing_meeting_ids.update([f.stem.replace('_request', '') for f in PROCESSED_PATH.rglob('*_request.json')])
    existing_meeting_ids.update([f.stem.replace('_request', '') for f in COMPLETED_PATH.rglob('*_request.json')])
    existing_meeting_ids.add(f"{datetime.now().strftime('%Y-%m-%d')}_internal-team") # Add a mock existing meeting ID for date collision test


    # 2. List Files from Google Drive (Fireflies/Transcripts) - USING MOCK DATA
    list_files_result = await mock_google_drive_list_files(GOOGLE_DRIVE_TRANSCRIPT_FOLDER_ID)
    
    if list_files_result.get('error'):
        print(f"Error listing files from Google Drive: {list_files_result['error']}")
        return

    gd_files = list_files_result.get('files', [])
    print(f"Found {len(gd_files)} files in (mock) Google Drive.")

    new_transcripts_detected = 0
    downloaded_files_count = 0
    queued_requests_count = 0
    skipped_duplicates_count = 0

    for gd_file in gd_files:
        gdrive_id = gd_file['id']
        filename = gd_file['name']
        mime_type = gd_file['mimeType']
        web_view_link = gd_file['webViewLink']
        # modified_time_str = gd_file['modifiedTime'] # Not used for this demo

        if gdrive_id in existing_gdrive_ids:
            print(f"Skipping duplicate: {filename} (gdrive_id: {gdrive_id}) already processed.")
            skipped_duplicates_count += 1
            continue

        if filename.startswith("[ZO-PROCESSED]"):
            print(f"Skipping {filename} as it's marked as processed in Google Drive.")
            skipped_duplicates_count += 1
            continue
        
        new_transcripts_detected += 1
        print(f"Processing new transcript: {filename} (gdrive_id: {gdrive_id})")

        # 3. Download to Transcript Directory - USING MOCK DATA
        download_path = TRANSCRIPTS_INBOX / f"{gdrive_id}.tmp" # Download to temp file first
        
        download_result = await mock_google_drive_download_file(gdrive_id, str(download_path))

        if download_result.get('error'):
            print(f"Error (MOCK) downloading {filename}: {download_result['error']}")
            continue

        downloaded_files_count += 1
        
        # Convert docx to txt if necessary
        actual_transcript_path = TRANSCRIPTS_INBOX / f"{gdrive_id}.txt"
        if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            print(f"Converting {filename} (docx) to plain text...")
            try:
                # Simulate pandoc conversion by just renaming and assuming conversion happened
                os.rename(download_path, actual_transcript_path) 
                # In a real scenario, default_api.run_bash_command(cmd=f"pandoc -s -t plain \"{download_path}\" -o \"{actual_transcript_path}\"") would be here
            except Exception as e:
                print(f"Error (MOCK) converting {filename} with pandoc: {e}")
                os.rename(download_path, actual_transcript_path) # Keep original if conversion fails
        else:
            os.rename(download_path, actual_transcript_path) # Rename .tmp to .txt

        transcript_content = ""
        if actual_transcript_path.exists():
            with open(actual_transcript_path, 'r') as f:
                transcript_content = f.read()

        # 4. Parse Filename and Classify
        date = extract_date_from_filename(filename)
        classification, participant_slug = classify_meeting_and_extract_participant(filename, transcript_content)
        
        # 5. Generate Meeting ID
        meeting_id = generate_meeting_id(date, classification, participant_slug, existing_meeting_ids)
        existing_meeting_ids.add(meeting_id) # Add to set to avoid future duplicates in this run

        # 6. Create Request File
        request_data = {
            "meeting_id": meeting_id,
            "classification": classification,
            "participants": participant_slug, # This can be refined later if needed
            "date": date,
            "gdrive_id": gdrive_id,
            "gdrive_link": web_view_link,
            "original_filename": filename,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "transcript_path": str(actual_transcript_path)
        }

        if classification == "external" and participant_slug != "unknown":
            request_data["external_participant"] = participant_slug

        request_file_path = INBOX_PATH / f"{meeting_id}_request.json"
        with open(request_file_path, 'w') as f:
            json.dump(request_data, f, indent=2)
        
        queued_requests_count += 1
        print(f"Created request file: {request_file_path}")

    print(f"--- Scan Results ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})---")
    print(f"✅ Detected {new_transcripts_detected} new transcripts")
    print(f"📥 Downloaded {downloaded_files_count} files")
    print(f"📋 Queued {queued_requests_count} requests")
    print(f"⏭️ Skipped {skipped_duplicates_count} duplicates")
    print("Scan complete.")

if __name__ == "__main__":
    asyncio.run(main())
