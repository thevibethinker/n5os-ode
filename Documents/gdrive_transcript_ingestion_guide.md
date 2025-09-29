# Google Drive Transcript Ingestion Extension

## Overview
This extension enables the consolidated transcript workflow to ingest transcripts directly from Google Drive folders, maintaining full N5OS compliance and MasterVoiceSchema integration.

## Architecture

### Core Components
1. **GoogleDriveConnector** - Handles Drive API interactions
2. **GoogleDriveTranscriptWorkflow** - Orchestrates batch processing
3. **Existing Workflow Integration** - Leverages consolidated_transcript_workflow.py

### Workflow Flow
```
Google Drive Folder → List Files → Download → Process → Save Outputs
       ↓              ↓          ↓         ↓          ↓
   Tool Call     File IDs   Local /tmp   Extract     Meetings/
   (list-files)            Files        Content     Directory
```

## Tool Integration

### Required Google Drive Tools
The extension uses these Google Drive app tools:

#### `google_drive-list-files`
Lists transcript files in a specified folder.

**Parameters:**
- `folderId`: Google Drive folder ID containing transcripts
- `filterText`: Optional text filter for file names
- `trashed`: Set to `false` to exclude deleted files

**Example Call:**
```json
{
  "tool_name": "google_drive-list-files",
  "configured_props": {
    "folderId": "1A2B3C4D5E6F7G8H9I0J",
    "filterText": "transcript",
    "trashed": false
  }
}
```

#### `google_drive-download-file`
Downloads individual transcript files to local /tmp directory.

**Parameters:**
- `fileId`: File ID from list operation
- `filePath`: Local destination path (/tmp/filename.txt)

**Example Call:**
```json
{
  "tool_name": "google_drive-download-file",
  "configured_props": {
    "fileId": "1abc123def456ghi789",
    "filePath": "/tmp/meeting_transcript_2025-09-15.txt"
  }
}
```

## Implementation Details

### File Processing Pipeline
1. **Discovery**: List all transcript files in target folder
2. **Retrieval**: Download each file to temporary local storage
3. **Processing**: Run consolidated workflow on each transcript
4. **Output**: Save results to structured directories
5. **Cleanup**: Remove temporary files

### Output Structure
```
Meetings/
├── gdrive_2025-09-15_meeting_transcript_2025-09-15_txt/
│   ├── content_map.json
│   ├── email_draft.md
│   ├── blurb_ticket_*.json
│   └── blurbs_summary.md
└── gdrive_2025-09-16_project_discussion_2025-09-16_txt/
    └── ...
```

### Telemetry and Logging
- **Batch-level metrics**: Total files, success/failure counts
- **File-level tracking**: Processing status per transcript
- **Error handling**: Graceful failure recovery
- **Performance monitoring**: Processing time and throughput

## Usage Examples

### Command Line Usage
```bash
# Process all transcripts in a Google Drive folder
python3 gdrive_transcript_workflow.py "1A2B3C4D5E6F7G8H9I0J"

# The folder ID can be obtained from Google Drive URL:
# https://drive.google.com/drive/folders/[FOLDER_ID]
```

### Programmatic Integration
```python
from gdrive_transcript_workflow import GoogleDriveTranscriptWorkflow

# Initialize workflow
workflow = GoogleDriveTranscriptWorkflow()

# Process folder
results = workflow.process_gdrive_folder(
    folder_id="1A2B3C4D5E6F7G8H9I0J",
    file_pattern="*.txt"
)

# Access results
print(f"Processed {results['batch_summary']['successful_files']} files")
```

## Configuration Options

### Voice Context Customization
```python
# Customize voice settings for the batch
voice_context = {
    "relationshipDepth": 2,  # 0-4 scale
    "medium": "email",       # email, spoken, dm, social
    "formality": "balanced", # casual, balanced, formal
    "ctaRigour": "balanced"  # soft, balanced, direct
}

results = workflow.process_gdrive_folder(
    folder_id="folder_id",
    voice_context=voice_context
)
```

### File Pattern Filtering
```python
# Process only specific file types
results = workflow.process_gdrive_folder(
    folder_id="folder_id",
    file_pattern="meeting_*.txt"  # Only files starting with "meeting_"
)
```

## Security and Compliance

### Data Handling
- **Temporary Storage**: Files downloaded to /tmp/ are automatically cleaned up
- **No Persistent Data**: Transcripts are not stored permanently in workspace
- **Access Control**: Uses authenticated Google Drive API credentials

### N5OS Compliance
- ✅ Telemetry logging for all operations
- ✅ Error handling with detailed error reporting
- ✅ Structured JSON outputs for all components
- ✅ Validation and audit trails
- ✅ Component modularity

## MasterVoiceSchema Integration

### Voice Fidelity
- **Version 1.3**: Full support for latest MasterVoiceSchema
- **Dynamic Calibration**: Context-aware greeting/sign-off generation
- **CTA Library**: Integrated call-to-action templates
- **Readability Guards**: Automatic formatting compliance

### Email Generation Features
- **Subject Line Auto-generation**: Per v10.6 specifications
- **Delay Sensitivity**: Automatic apology for >2 day delays
- **Resonance Integration**: Extracts and incorporates emotional context
- **Traditional Formatting**: Paragraphs and bullets only

## Batch Processing Features

### Parallel Processing
- Files are processed sequentially to maintain resource control
- Individual file failures don't stop batch processing
- Detailed per-file success/failure reporting

### Result Aggregation
- **Batch Summary**: High-level statistics and metrics
- **Individual Results**: Detailed processing results per file
- **Telemetry Data**: Complete audit trail for compliance

## Error Handling and Recovery

### Common Error Scenarios
1. **Folder Not Found**: Invalid folder ID or access denied
2. **File Download Failure**: Network issues or permission problems
3. **Processing Errors**: Malformed transcript content
4. **Output Directory Issues**: Disk space or permission problems

### Recovery Mechanisms
- **Graceful Degradation**: Continue processing other files on individual failures
- **Detailed Logging**: Complete error context for troubleshooting
- **Cleanup on Failure**: Remove partial outputs and temporary files

## Performance Considerations

### Optimization Strategies
- **Incremental Processing**: Process files as they're discovered
- **Memory Management**: Stream processing for large transcripts
- **Rate Limiting**: Respect Google Drive API quotas
- **Caching**: Avoid re-downloading recently processed files

### Monitoring Metrics
- **Throughput**: Files processed per minute
- **Success Rate**: Percentage of successful processing
- **Error Patterns**: Common failure modes for optimization
- **Resource Usage**: Memory and disk utilization

## Integration with Existing Systems

### Meeting Management
- **Directory Structure**: Organized by date and source
- **File Naming**: Consistent naming conventions
- **Metadata Tracking**: Complete processing history

### Workflow Orchestration
- **Modular Design**: Easy integration with other workflows
- **Configurable Parameters**: Flexible deployment options
- **Standard Interfaces**: JSON-based input/output formats

## Future Enhancements

### Planned Features
1. **Real-time Monitoring**: Live processing status dashboard
2. **Advanced Filtering**: Date range and content-based filtering
3. **Batch Scheduling**: Automated periodic processing
4. **Integration Hooks**: Webhook notifications for processing completion
5. **Multi-format Support**: Support for additional file formats (DOCX, PDF)

### Scalability Improvements
1. **Concurrent Processing**: Parallel file processing
2. **Distributed Execution**: Multi-instance processing
3. **Queue Management**: Advanced job queuing and prioritization
4. **Load Balancing**: Intelligent resource allocation

## Troubleshooting Guide

### Common Issues

#### "No files found in folder"
- Verify folder ID is correct
- Check folder permissions
- Ensure files match the specified pattern

#### "Download failed"
- Verify file permissions
- Check Google Drive API quota
- Ensure stable network connection

#### "Processing error"
- Validate transcript file format
- Check for special characters or encoding issues
- Review error logs for specific failure details

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG
python3 gdrive_transcript_workflow.py "folder_id"
```

## Conclusion

This Google Drive extension transforms the transcript ingestion workflow from local file processing to cloud-based batch processing, maintaining all existing functionality while adding powerful new capabilities for large-scale transcript management.

The integration preserves N5OS compliance, MasterVoiceSchema fidelity, and all existing output formats while providing enterprise-grade scalability and automation features.</content>
</xai:function_call<parameter name="target_file">/home/workspace/gdrive_transcript_ingestion_guide.md