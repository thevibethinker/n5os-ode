Validation Report: /home/workspace/N5/scripts
Files scanned: 369
Errors: 291
Warnings: 153

ERRORS:
  [stub] sync_to_drive.py:211 - Stub implementation detected
  [stub] sync_to_drive_impl.py:49 - Stub implementation detected
  [stub] sync_to_drive_impl.py:73 - Stub implementation detected
  [stub] sync_to_drive_impl.py:90 - Stub implementation detected
  [stub] sync_to_drive_impl.py:124 - Stub implementation detected
  [stub] sync_to_drive_impl.py:147 - Stub implementation detected
  [stub] test_validation.py:26 - Stub implementation detected
  [stub] meeting_orchestrator_v1_DEPRECATED.py:321 - Stub implementation detected
  [stub] llm_client_real.py:55 - Stub implementation detected
  [broken_import] conversation_registry.py:15 - Cannot resolve module: contextlib
  [broken_import] n5_test_modules_flows.py:11 - Cannot resolve import: tempfile
  [broken_import] reflection_block_generator.py:16 - Cannot resolve import: shutil
  [broken_import] n5_conversation_end.py:13 - Cannot resolve import: shutil
  [broken_import] crm_migrate_profiles.py:18 - Cannot resolve import: yaml
  [broken_import] crm_migrate_profiles.py:420 - Cannot resolve import: shutil
  [broken_import] n5_schema_validation.py:12 - Cannot resolve module: jsonschema
  [broken_import] n5_system_timeline_add.py:9 - Cannot resolve import: uuid
  [broken_import] safe_stakeholder_updater.py:15 - Cannot resolve import: shutil
  [broken_import] safe_stakeholder_updater.py:20 - Cannot resolve import: difflib
  [broken_import] safe_stakeholder_updater.py:21 - Cannot resolve import: hashlib
  [broken_import] careerspan_insights_extractor.py:20 - Cannot resolve import: pytz
  [broken_import] n5_text_to_list_processor.py:10 - Cannot resolve import: uuid
  [broken_import] n5_text_to_list_processor.py:15 - Cannot resolve module: jsonschema
  [broken_import] read_workflow_metadata.py:6 - Cannot resolve import: yaml
  [broken_import] closure_tracker.py:18 - Cannot resolve import: jsonschema
  [broken_import] closure_tracker.py:19 - Cannot resolve module: jsonschema
  [broken_import] n5_secrets.py:15 - Cannot resolve module: cryptography.fernet
  [broken_import] n5_secrets.py:114 - Cannot resolve import: inspect
  [broken_import] message_queue.py:16 - Cannot resolve import: uuid
  [broken_import] n5_convert_prompt.py:27 - Cannot resolve import: shutil
  [broken_import] research_prompt_generator.py:18 - Cannot resolve import: pytz
  [broken_import] research_prompt_generator.py:46 - Cannot resolve import: pyperclip
  [broken_import] n5_knowledge_ingest.py:28 - Cannot resolve import: uuid
  [broken_import] n5_knowledge_ingest.py:36 - Cannot resolve module: scripts.direct_ingestion_mechanism
  [broken_import] n5_knowledge_ingest.py:37 - Cannot resolve module: scripts.n5_knowledge_conflict_resolution_interactive
  [broken_import] n5_knowledge_ingest.py:38 - Cannot resolve module: scripts.n5_knowledge_adaptive_suggestions
  [broken_import] n5_meeting_approve.py:275 - Cannot resolve import: time
  [broken_import] n5_schedule_wrapper.py:13 - Cannot resolve import: time
  [broken_import] n5_schedule_wrapper.py:14 - Cannot resolve import: fcntl
  [broken_import] git_change_checker_v2.py:20 - Cannot resolve module: fnmatch
  [broken_import] n5_lessons_review.py:19 - Cannot resolve import: shutil
  [broken_import] n5_document_redistillation.py:12 - Cannot resolve module: functions
  [broken_import] meeting_state_manager.py:9 - Cannot resolve import: shutil
  [broken_import] meeting_state_manager.py:14 - Cannot resolve import: pytz
  [broken_import] n5_index_rebuild.py:6 - Cannot resolve import: hashlib
  [broken_import] n5_index_rebuild.py:8 - Cannot resolve import: fcntl
  [broken_import] n5_index_rebuild.py:11 - Cannot resolve module: jsonschema
  [broken_import] n5_job_source_extract.py:11 - Cannot resolve import: gspread
  [broken_import] n5_job_source_extract.py:12 - Cannot resolve module: oauth2client.service_account
  [broken_import] n5_job_source_extract.py:16 - Cannot resolve module: lib.secrets
  [broken_import] test_lessons_system.py:9 - Cannot resolve import: uuid
  [broken_import] n5_bootstrap_advisor_server.py:10 - Cannot resolve module: http.server
  [broken_import] listclassifier.py:4 - Cannot resolve module: urllib.parse
  [broken_import] duplicate_scanner.py:18 - Cannot resolve import: hashlib
  [broken_import] extract_meeting_actions.py:17 - Cannot resolve module: calendar_scheduler
  [broken_import] direct_ingestion_mechanism.py:12 - Cannot resolve import: uuid
  [broken_import] digest_integration.py:9 - Cannot resolve import: pytz
  [broken_import] front_matter_manager_part2.py:4 - Cannot resolve import: tempfile
  [broken_import] front_matter_manager_part2.py:5 - Cannot resolve import: textwrap
  [broken_import] n5_workspace_maintenance.py:9 - Cannot resolve import: shutil
  [broken_import] n5_workspace_maintenance.py:13 - Cannot resolve import: hashlib
  [broken_import] generate_dashboard.py:12 - Cannot resolve import: pytz
  [broken_import] n5_lessons_extract.py:19 - Cannot resolve import: uuid
  [broken_import] n5_knowledge_conflict_resolution_llm.py:13 - Cannot resolve module: functions
  [broken_import] n5_knowledge_add.py:5 - Cannot resolve import: uuid
  [broken_import] summarize_segments.py:8 - Cannot resolve import: aiohttp
  [broken_import] email_validation_learner.py:24 - Cannot resolve import: difflib
  [broken_import] sync_to_drive.py:28 - Cannot resolve import: hashlib
  [broken_import] meeting_duplicate_detector.py:9 - Cannot resolve import: hashlib
  [broken_import] stakeholder_profile_manager.py:13 - Cannot resolve import: pytz
  [broken_import] strategy_evolution_tracker.py:20 - Cannot resolve import: math
  [broken_import] file_backup.py:7 - Cannot resolve import: shutil
  [broken_import] n5_deployment_packager.py:10 - Cannot resolve import: base64
  [broken_import] n5_deployment_packager.py:11 - Cannot resolve import: hashlib
  [broken_import] n5_deployment_packager.py:15 - Cannot resolve import: stat
  [broken_import] n5_workspace_root_cleanup.py:12 - Cannot resolve import: shutil
  [broken_import] n5_workspace_root_cleanup.py:16 - Cannot resolve import: hashlib
  [broken_import] meeting_prep_digest.py:21 - Cannot resolve import: pytz
  [broken_import] n5_docgen.py:13 - Cannot resolve module: jsonschema
  [broken_import] generate_internal_blocks.py:34 - Cannot resolve module: stakeholder_classifier
  [broken_import] n5_lists_create.py:5 - Cannot resolve import: uuid
  [broken_import] n5_lists_create.py:9 - Cannot resolve module: jsonschema
  [broken_import] gmail_fetch_staging.py:18 - Cannot resolve import: base64
  [broken_import] gmail_fetch_staging.py:22 - Cannot resolve module: email.utils
  [broken_import] gmail_fetch_staging.py:25 - Cannot resolve module: google.oauth2
  [broken_import] gmail_fetch_staging.py:26 - Cannot resolve module: googleapiclient.discovery
  [broken_import] gmail_fetch_staging.py:27 - Cannot resolve module: googleapiclient.errors
  [broken_import] gmail_fetch_staging.py:31 - Cannot resolve module: lib.secrets
  [broken_import] n5_linkedin_intel.py:18 - Cannot resolve module: bs4
  [broken_import] file_watcher.py:8 - Cannot resolve import: time
  [broken_import] file_watcher.py:9 - Cannot resolve import: hashlib
  [broken_import] inbox_analyzer.py:11 - Cannot resolve import: mimetypes
  [broken_import] bootstrap_conversation_client.py:10 - Cannot resolve import: time
  [broken_import] bootstrap_conversation_client.py:16 - Cannot resolve import: requests
  [broken_import] monitor_health.py:11 - Cannot resolve import: pytz
  [broken_import] monitor_health.py:173 - Cannot resolve import: shutil
  [broken_import] migrate_registry_columns.py:14 - Cannot resolve import: shutil
  [broken_import] n5_deployment_sender.py:16 - Cannot resolve import: requests
  [broken_import] test_conversation_end.py:16 - Cannot resolve import: tempfile
  [broken_import] test_conversation_end.py:17 - Cannot resolve import: shutil
  [broken_import] rotate_logs.py:8 - Cannot resolve import: gzip
  [broken_import] rotate_logs.py:9 - Cannot resolve import: shutil
  [broken_import] rotate_logs.py:12 - Cannot resolve import: pytz
  [broken_import] n5_conversation_end_v2.py:270 - Cannot resolve import: shutil
  [broken_import] meeting_monitor.py:9 - Cannot resolve import: time
  [broken_import] meeting_monitor.py:13 - Cannot resolve import: pytz
  [broken_import] session_state_manager.py:16 - Cannot resolve import: pytz
  [broken_import] validate_meeting_folder_names.py:22 - Cannot resolve import: shutil
  [broken_import] integration_test_runner.py:104 - Cannot resolve import: time
  [broken_import] integration_test_runner.py:186 - Cannot resolve import: time
  [broken_import] n5_unsent_followups_digest.py:20 - Cannot resolve module: difflib
  [broken_import] meeting_transcript_watcher.py:12 - Cannot resolve import: hashlib
  [broken_import] background_email_scanner.py:24 - Cannot resolve import: base64
  [broken_import] background_email_scanner.py:28 - Cannot resolve module: email.utils
  [broken_import] background_email_scanner.py:32 - Cannot resolve module: google.oauth2
  [broken_import] background_email_scanner.py:33 - Cannot resolve module: googleapiclient.discovery
  [broken_import] background_email_scanner.py:34 - Cannot resolve module: googleapiclient.errors
  [broken_import] background_email_scanner.py:70 - Cannot resolve module: lib.secrets
  [broken_import] n5_lists_pin.py:7 - Cannot resolve module: jsonschema
  [broken_import] review_manager.py:13 - Cannot resolve import: hashlib
  [broken_import] review_manager.py:18 - Cannot resolve import: secrets
  [broken_import] review_manager.py:19 - Cannot resolve import: jsonschema
  [broken_import] n5_lists_add.py:7 - Cannot resolve import: uuid
  [broken_import] n5_lists_add.py:13 - Cannot resolve module: jsonschema
  [broken_import] howie_verbal_signal_detector.py:14 - Cannot resolve module: enum
  [broken_import] n5_bootstrap_conversational_server.py:10 - Cannot resolve import: uuid
  [broken_import] n5_bootstrap_conversational_server.py:12 - Cannot resolve module: http.server
  [broken_import] gdrive_transcript_workflow.py:23 - Cannot resolve import: time
  [broken_import] gdrive_transcript_workflow.py:27 - Cannot resolve import: hashlib
  [broken_import] reflection_synthesizer_v2.py:35 - Cannot resolve import: glob
  [broken_import] full_sync_to_main.py:7 - Cannot resolve import: shutil
  [broken_import] meeting_core_generator.py:22 - Cannot resolve module: stakeholder_classifier
  [broken_import] meeting_core_generator.py:52 - Cannot resolve import: tempfile
  [broken_import] meeting_auto_processor.py:12 - Cannot resolve import: time
  [broken_import] monitor_action_approvals.py:7 - Cannot resolve import: time
  [broken_import] conversation_end_analyzer.py:18 - Cannot resolve import: tempfile
  [broken_import] conversation_end_analyzer.py:19 - Cannot resolve import: shutil
  [broken_import] conversation_end_analyzer.py:410 - Cannot resolve import: tempfile
  [broken_import] conversation_end_analyzer.py:411 - Cannot resolve import: shutil
  [broken_import] demo_priority_3.py:10 - Cannot resolve import: pytz
  [broken_import] n5_run_record.py:12 - Cannot resolve import: uuid
  [broken_import] n5_run_record.py:13 - Cannot resolve import: hashlib
  [broken_import] n5_knowledge_adaptive_suggestions.py:13 - Cannot resolve module: functions
  [broken_import] n5_lists_move.py:5 - Cannot resolve import: uuid
  [broken_import] n5_lists_move.py:8 - Cannot resolve module: jsonschema
  [broken_import] convo_supervisor.py:34 - Cannot resolve import: difflib
  [broken_import] n5_export_core.py:12 - Cannot resolve import: shutil
  [broken_import] n5_export_core.py:17 - Cannot resolve import: yaml
  [broken_import] n5_export_core.py:18 - Cannot resolve import: glob
  [broken_import] n5_lists_monitor.py:36 - Cannot resolve module: jsonschema
  [broken_import] n5_lists_set.py:7 - Cannot resolve module: jsonschema
  [broken_import] backfill_followup_metadata.py:12 - Cannot resolve import: shutil
  [broken_import] n5_compat_scan.py:26 - Cannot resolve import: platform
  [broken_import] n5_compat_scan.py:27 - Cannot resolve import: shutil
  [broken_import] n5_compat_scan.py:28 - Cannot resolve import: socket
  [broken_import] front_matter_manager.py:7 - Cannot resolve import: yaml
  [broken_import] front_matter_manager.py:8 - Cannot resolve import: hashlib
  [broken_import] front_matter_manager.py:16 - Cannot resolve import: tempfile
  [broken_import] front_matter_manager.py:17 - Cannot resolve import: textwrap
  [broken_import] n5_knowledge_conflict_resolution_interactive.py:16 - Cannot resolve module: functions
  [broken_import] process_meeting_transcript.py:67 - Cannot resolve import: shutil
  [broken_import] bulletin_generator.py:108 - Cannot resolve module: fnmatch
  [broken_import] bulletin_generator.py:188 - Cannot resolve module: hashlib
  [broken_import] bulletin_generator.py:189 - Cannot resolve module: time
  [broken_import] recipe_index_builder.py:25 - Cannot resolve import: yaml
  [broken_import] conversation_end_executor.py:13 - Cannot resolve import: shutil
  [broken_import] conversation_end_executor.py:17 - Cannot resolve module: enum
  [broken_import] conversation_end_executor.py:478 - Cannot resolve import: tempfile
  [broken_import] content_library.py:29 - Cannot resolve module: __future__
  [broken_import] meeting_api_integrator.py:12 - Cannot resolve import: pytz
  [broken_import] timeline_automation_module.py:11 - Cannot resolve import: uuid
  [broken_import] n5_index_update.py:6 - Cannot resolve import: hashlib
  [broken_import] n5_index_update.py:7 - Cannot resolve import: mimetypes
  [broken_import] n5_index_update.py:8 - Cannot resolve import: fcntl
  [broken_import] n5_index_update.py:11 - Cannot resolve module: jsonschema
  [broken_import] deploy_meeting_monitor.py:11 - Cannot resolve import: pytz
  [syntax] system_upgrades_add_fixed.py:1 - Syntax error: unexpected indent
  [broken_import] fix_meeting_duplication.py:8 - Cannot resolve import: shutil
  [broken_import] deliverable_orchestrator.py:266 - Cannot resolve module: llm_utils
  [broken_import] sync_to_main.py:8 - Cannot resolve import: shutil
  [broken_import] sync_to_main.py:11 - Cannot resolve import: hashlib
  [broken_import] n5_thread_export.py:14 - Cannot resolve import: shutil
  [broken_import] n5_thread_export.py:19 - Cannot resolve import: tempfile
  [broken_import] n5_thread_export.py:22 - Cannot resolve module: jsonschema
  [broken_import] n5_thread_export.py:992 - Cannot resolve import: tempfile
  [broken_import] send_sms_notification.py:52 - Cannot resolve import: time
  [broken_import] core_audit.py:10 - Cannot resolve import: time
  [broken_import] test_conversation_api.py:10 - Cannot resolve import: time
  [broken_import] test_conversation_api.py:14 - Cannot resolve import: requests
  [broken_import] n5_incantum.py:7 - Cannot resolve module: __future__
  [broken_import] n5_incantum.py:17 - Cannot resolve module: rapidfuzz
  [broken_import] run_direct_ingestion.py:14 - Cannot resolve module: scripts.direct_ingestion_mechanism
  [broken_import] commands_chronological_setup.py:20 - Cannot resolve import: shutil
  [broken_import] inbox_router.py:11 - Cannot resolve import: shutil
  [broken_import] timeline_automation.py:11 - Cannot resolve import: uuid
  [broken_import] consolidated_transcript_workflow.py:21 - Cannot resolve import: time
  [broken_import] consolidated_transcript_workflow.py:26 - Cannot resolve import: hashlib
  [broken_import] system_upgrades_add.py:10 - Cannot resolve import: uuid
  [broken_import] system_upgrades_add.py:16 - Cannot resolve import: shutil
  [broken_import] system_upgrades_add.py:17 - Cannot resolve import: difflib
  [broken_import] system_upgrades_add.py:18 - Cannot resolve module: lib
  [broken_import] system_upgrades_add.py:20 - Cannot resolve module: difflib
  [broken_import] system_upgrades_add.py:21 - Cannot resolve module: system_upgrades_backup_manager
  [broken_import] system_upgrades_add.py:22 - Cannot resolve import: jsonschema
  [broken_import] system_upgrades_add.py:451 - Cannot resolve module: system_upgrades_backup_manager
  [broken_import] n5_test_safety.py:11 - Cannot resolve import: tempfile
  [broken_import] social_post_lib.py:10 - Cannot resolve import: hashlib
  [broken_import] n5_archive_threads.py:19 - Cannot resolve import: shutil
  [broken_import] n5_archive_threads.py:20 - Cannot resolve import: tarfile
  [broken_import] background_contact_enrichment.py:11 - Cannot resolve import: glob
  [broken_import] n5_git_audit.py:5 - Cannot resolve import: shlex
  [broken_import] consolidated_transcript_workflow_v2.py:21 - Cannot resolve import: time
  [broken_import] consolidated_transcript_workflow_v2.py:25 - Cannot resolve import: hashlib
  [broken_import] gmail_monitor.py:14 - Cannot resolve import: email
  [broken_import] gmail_monitor.py:15 - Cannot resolve module: email.utils
  [broken_import] root_cleanup.py:11 - Cannot resolve import: fnmatch
  [broken_import] root_cleanup.py:12 - Cannot resolve import: shutil
  [broken_import] meeting_ai_deduplicator.py:183 - Cannot resolve module: llm_helper
  [broken_import] n5_import_prompt.py:14 - Cannot resolve import: shutil
  [broken_import] tally_manager.py:18 - Cannot resolve import: uuid
  [broken_import] tally_manager.py:22 - Cannot resolve import: requests
  [broken_import] front_matter_manager_part1.py:7 - Cannot resolve import: yaml
  [broken_import] front_matter_manager_part1.py:8 - Cannot resolve import: hashlib
  [broken_import] email_corrections.py:16 - Cannot resolve module: difflib
  [broken_import] slack_send.py:8 - Cannot resolve module: slack_sdk
  [broken_import] slack_send.py:9 - Cannot resolve module: slack_sdk.errors
  [broken_import] slack_send.py:13 - Cannot resolve module: lib.secrets
  [broken_import] slack_read.py:9 - Cannot resolve module: slack_sdk
  [broken_import] slack_read.py:10 - Cannot resolve module: slack_sdk.errors
  [broken_import] slack_read.py:14 - Cannot resolve module: lib.secrets
  [broken_import] google_auth.py:12 - Cannot resolve module: lib.secrets
  [broken_import] google_auth.py:43 - Cannot resolve module: google.oauth2
  [broken_import] google_auth.py:44 - Cannot resolve module: googleapiclient.discovery
  [broken_import] test_validation.py:7 - Cannot resolve import: tempfile
  [broken_import] test_validation.py:96 - Cannot resolve import: shutil
  [broken_import] chunk2_scoper.py:12 - Cannot resolve import: time
  [broken_import] chunk6_exporter.py:13 - Cannot resolve import: time
  [broken_import] chunk3_generator.py:12 - Cannot resolve import: time
  [broken_import] ux_enhancer.py:12 - Cannot resolve import: time
  [broken_import] ux_enhancer.py:264 - Cannot resolve module: chunk1_parser
  [broken_import] ux_enhancer.py:277 - Cannot resolve module: chunk2_scoper
  [broken_import] performance_optimizer.py:11 - Cannot resolve import: pickle
  [broken_import] performance_optimizer.py:12 - Cannot resolve import: time
  [broken_import] performance_optimizer.py:17 - Cannot resolve import: hashlib
  [broken_import] performance_optimizer.py:249 - Cannot resolve module: chunk1_parser
  [broken_import] performance_optimizer.py:264 - Cannot resolve module: chunk2_scoper
  [syntax] test_data_complete.py:69 - Syntax error: unterminated triple-quoted string literal (detected at line 69)
  [broken_import] telemetry_collector.py:11 - Cannot resolve import: time
  [broken_import] chunk5_resolver.py:13 - Cannot resolve import: time
  [broken_import] chunk5_resolver.py:17 - Cannot resolve import: difflib
  [broken_import] chunk1_parser.py:14 - Cannot resolve import: time
  [broken_import] chunk4_validator.py:13 - Cannot resolve import: time
  [broken_import] chunk4_validator.py:223 - Cannot resolve import: random
  [syntax] test_data_generator.py:69 - Syntax error: unterminated triple-quoted string literal (detected at line 69)
  [broken_import] system_upgrades_sync.py:3 - Cannot resolve import: fcntl
  [broken_import] system_upgrades_sync.py:4 - Cannot resolve import: tempfile
  [broken_import] system_upgrades_sync.py:5 - Cannot resolve module: contextlib
  [broken_import] system_upgrades_validator.py:11 - Cannot resolve module: jsonschema
  [broken_import] system_upgrades_validator.py:12 - Cannot resolve import: jsonschema
  [broken_import] llm_helper.py:17 - Cannot resolve import: time
  [broken_import] chunk3_generator.py:12 - Cannot resolve import: time
  [broken_import] chunk2_scoper.py:12 - Cannot resolve import: time
  [broken_import] ux_enhancer.py:12 - Cannot resolve import: time
  [broken_import] ux_enhancer.py:264 - Cannot resolve module: chunk1_parser
  [broken_import] ux_enhancer.py:277 - Cannot resolve module: chunk2_scoper
  [syntax] test_data_generator.py:69 - Syntax error: unterminated triple-quoted string literal (detected at line 69)
  [broken_import] chunk1_parser.py:14 - Cannot resolve import: time
  [broken_import] chunk4_validator.py:13 - Cannot resolve import: time
  [broken_import] chunk4_validator.py:223 - Cannot resolve import: random
  [broken_import] telemetry_collector.py:11 - Cannot resolve import: time
  [syntax] test_data_complete.py:69 - Syntax error: unterminated triple-quoted string literal (detected at line 69)
  [syntax] simple_test_gen.py:17 - Syntax error: unterminated triple-quoted string literal (detected at line 17)
  [broken_import] chunk5_resolver.py:13 - Cannot resolve import: time
  [broken_import] chunk5_resolver.py:17 - Cannot resolve import: difflib
  [broken_import] chunk6_exporter.py:13 - Cannot resolve import: time
  [broken_import] performance_optimizer.py:11 - Cannot resolve import: pickle
  [broken_import] performance_optimizer.py:12 - Cannot resolve import: time
  [broken_import] performance_optimizer.py:17 - Cannot resolve import: hashlib
  [broken_import] performance_optimizer.py:249 - Cannot resolve module: chunk1_parser
  [broken_import] performance_optimizer.py:264 - Cannot resolve module: chunk2_scoper
  [broken_import] weekly_cleanup.py:10 - Cannot resolve import: shutil
  [broken_import] meeting_orchestrator_v1_DEPRECATED.py:10 - Cannot resolve import: hashlib
  [broken_import] meeting_orchestrator_v1_DEPRECATED.py:11 - Cannot resolve import: uuid
  [broken_import] llm_client.py:8 - Cannot resolve import: tempfile
  [broken_import] meeting_info_extractor.py:11 - Cannot resolve module: llm_utils
  [broken_import] llm_client_real.py:8 - Cannot resolve import: tempfile
  [broken_import] meeting_orchestrator.py:30 - Cannot resolve module: llm_utils
  [broken_import] meeting_orchestrator.py:329 - Cannot resolve module: llm_utils
  [broken_import] xp_system.py:18 - Cannot resolve import: math
  [broken_import] rpi_calculator.py:190 - Cannot resolve import: math
  [broken_import] meeting_scanner_integrated.py:15 - Cannot resolve import: meeting_scanner

WARNINGS:
  [placeholder] conversation_registry.py:723 - Placeholder comment found
  [placeholder] conversation_registry.py:730 - Placeholder comment found
  [placeholder] reflection_block_generator.py:113 - Placeholder comment found
  [placeholder] reflection_block_generator.py:116 - Placeholder comment found
  [placeholder] n5_conversation_end.py:639 - Placeholder comment found
  [placeholder] n5_conversation_end.py:639 - Placeholder comment found
  [placeholder] n5_conversation_end.py:646 - Placeholder comment found
  [placeholder] n5_conversation_end.py:651 - Placeholder comment found
  [placeholder] n5_conversation_end.py:683 - Placeholder comment found
  [placeholder] n5_conversation_end.py:696 - Placeholder comment found
  [placeholder] n5_conversation_end.py:701 - Placeholder comment found
  [placeholder] n5_conversation_end.py:713 - Placeholder comment found
  [placeholder] n5_conversation_end.py:720 - Placeholder comment found
  [placeholder] n5_conversation_end.py:724 - Placeholder comment found
  [placeholder] n5_conversation_end.py:941 - Placeholder comment found
  [placeholder] n5_conversation_end.py:1612 - Placeholder comment found
  [placeholder] n5_conversation_end.py:1701 - Placeholder comment found
  [placeholder] n5_conversation_end.py:1835 - Placeholder comment found
  [placeholder] careerspan_insights_extractor.py:262 - Placeholder comment found
  [placeholder] reflection_ingest_bridge.py:93 - Placeholder comment found
  [placeholder] reflection_ingest_bridge.py:115 - Placeholder comment found
  [placeholder] reflection_ingest_bridge.py:139 - Placeholder comment found
  [placeholder] reflection_ingest_bridge.py:165 - Placeholder comment found
  [placeholder] spawn_worker.py:79 - Placeholder comment found
  [placeholder] spawn_worker.py:81 - Placeholder comment found
  [placeholder] scheduled_email_scan.py:35 - Placeholder comment found
  [placeholder] integrate_email_with_b25.py:165 - Placeholder comment found
  [placeholder] integrate_email_with_b25.py:186 - Placeholder comment found
  [placeholder] research_prompt_generator.py:131 - Placeholder comment found
  [placeholder] n5_knowledge_ingest.py:279 - Placeholder comment found
  [placeholder] n5_knowledge_ingest.py:294 - Placeholder comment found
  [placeholder] sync_mechanism.py:77 - Placeholder comment found
  [placeholder] sync_mechanism.py:133 - Placeholder comment found
  [placeholder] zobridge_bootstrap_sender.py:175 - Placeholder comment found
  [placeholder] meeting_prep_digest_v2.py:39 - Placeholder comment found
  [placeholder] meeting_prep_digest_v2.py:128 - Placeholder comment found
  [placeholder] n5_networking_event_process.py:905 - Placeholder comment found
  [placeholder] n5_knowledge_adaptive_suggestions_expand.py:81 - Placeholder comment found
  [placeholder] n5_knowledge_adaptive_suggestions_expand.py:82 - Placeholder comment found
  [placeholder] n5_knowledge_adaptive_suggestions_expand.py:85 - Placeholder comment found
  [placeholder] n5_knowledge_adaptive_suggestions_expand.py:92 - Placeholder comment found
  [placeholder] n5_knowledge_adaptive_suggestions_expand.py:95 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:49 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:50 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:52 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:61 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:118 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:125 - Placeholder comment found
  [placeholder] n5_lessons_extract.py:292 - Placeholder comment found
  [placeholder] akiflow_push.py:93 - Placeholder comment found
  [placeholder] sync_to_drive.py:197 - Placeholder comment found
  [placeholder] strategy_evolution_tracker.py:256 - Placeholder comment found
  [placeholder] meeting_prep_digest.py:301 - Placeholder comment found
  [placeholder] realtime_state_tracker.py:221 - Placeholder comment found
  [placeholder] realtime_state_tracker.py:258 - Placeholder comment found
  [placeholder] n5_follow_up_email_generator.py:429 - Placeholder comment found
  [placeholder] n5_knowledge_conflict_resolution.py:71 - Placeholder comment found
  [placeholder] update_personal_intelligence.py:76 - Placeholder comment found
  [placeholder] update_personal_intelligence.py:337 - Placeholder comment found
  [placeholder] inbox_analyzer.py:63 - Placeholder comment found
  [placeholder] inbox_analyzer.py:85 - Placeholder comment found
  [placeholder] inbox_analyzer.py:99 - Placeholder comment found
  [placeholder] validate_digest_output.py:5 - Placeholder comment found
  [placeholder] validate_digest_output.py:11 - Placeholder comment found
  [placeholder] validate_digest_output.py:17 - Placeholder comment found
  [placeholder] validate_digest_output.py:43 - Placeholder comment found
  [placeholder] validate_digest_output.py:46 - Placeholder comment found
  [placeholder] session_state_manager.py:280 - Placeholder comment found
  [placeholder] reflection_worker.py:95 - Placeholder comment found
  [placeholder] reflection_worker.py:96 - Placeholder comment found
  [placeholder] meeting_transcript_watcher.py:109 - Placeholder comment found
  [placeholder] conversation_resync.py:73 - Placeholder comment found
  [placeholder] conversation_resync.py:80 - Placeholder comment found
  [placeholder] background_email_scanner.py:294 - Placeholder comment found
  [placeholder] background_email_scanner.py:324 - Placeholder comment found
  [placeholder] enrich_stakeholder_contact.py:365 - Placeholder comment found
  [placeholder] enrich_stakeholder_contact.py:374 - Placeholder comment found
  [placeholder] enrich_stakeholder_contact.py:388 - Placeholder comment found
  [placeholder] meeting_core_generator.py:62 - Placeholder comment found
  [placeholder] process_email_staging_llm.py:60 - Placeholder comment found
  [placeholder] process_email_staging_llm.py:169 - Placeholder comment found
  [placeholder] reflection_auto_ingest.py:43 - Placeholder comment found
  [placeholder] reflection_ingest.py:43 - Placeholder comment found
  [placeholder] reflection_ingest.py:61 - Placeholder comment found
  [placeholder] reflection_ingest.py:80 - Placeholder comment found
  [placeholder] reflection_ingest.py:85 - Placeholder comment found
  [placeholder] n5_knowledge_conflict_resolution_interactive.py:94 - Placeholder comment found
  [placeholder] n5_knowledge_conflict_resolution_interactive.py:97 - Placeholder comment found
  [placeholder] n5_placeholder_scan.py:3 - Placeholder comment found
  [placeholder] n5_placeholder_scan.py:76 - Placeholder comment found
  [placeholder] n5_placeholder_scan.py:100 - Placeholder comment found
  [placeholder] n5_placeholder_scan.py:199 - Placeholder comment found
  [placeholder] n5_placeholder_scan.py:209 - Placeholder comment found
  [placeholder] reflection_pipeline.py:30 - Placeholder comment found
  [placeholder] auto_create_stakeholder_profiles.py:44 - Placeholder comment found
  [placeholder] auto_create_stakeholder_profiles.py:138 - Placeholder comment found
  [placeholder] orchestrator.py:283 - Placeholder comment found
  [placeholder] orchestrator.py:287 - Placeholder comment found
  [placeholder] generate_followup_email_draft.py:51 - Placeholder comment found
  [placeholder] generate_followup_email_draft.py:144 - Placeholder comment found
  [placeholder] reflection_ingest_v2.py:94 - Placeholder comment found
  [placeholder] strategic_partner_session.py:123 - Placeholder comment found
  [placeholder] warm_intro_generator.py:236 - Placeholder comment found
  [placeholder] deliverable_orchestrator.py:60 - Placeholder comment found
  [placeholder] post_write_digest_scan.py:5 - Placeholder comment found
  [placeholder] post_write_digest_scan.py:42 - Placeholder comment found
  [placeholder] post_write_digest_scan.py:43 - Placeholder comment found
  [placeholder] file_flow_router.py:87 - Placeholder comment found
  [placeholder] file_flow_router.py:112 - Placeholder comment found
  [placeholder] gmail_monitor.py:99 - Placeholder comment found
  [placeholder] gmail_monitor.py:103 - Placeholder comment found
  [placeholder] n5_gfetch.py:55 - Placeholder comment found
  [placeholder] n5_gfetch.py:69 - Placeholder comment found
  [placeholder] n5_gfetch.py:110 - Placeholder comment found
  [placeholder] n5_gfetch.py:119 - Placeholder comment found
  [placeholder] email_body_generator.py:247 - Placeholder comment found
  [placeholder] tally_manager.py:139 - Placeholder comment found
  [placeholder] tally_manager.py:190 - Placeholder comment found
  [placeholder] validation.py:125 - Placeholder comment found
  [placeholder] validation.py:140 - Placeholder comment found
  [placeholder] validation.py:147 - Placeholder comment found
  [placeholder] validation.py:161 - Placeholder comment found
  [placeholder] sweep.py:41 - Placeholder comment found
  [placeholder] sweep.py:59 - Placeholder comment found
  [placeholder] test_validation.py:36 - Placeholder comment found
  [placeholder] test_validation.py:40 - Placeholder comment found
  [placeholder] chunk1_parser.py:193 - Placeholder comment found
  [placeholder] chunk1_parser.py:193 - Placeholder comment found
  [placeholder] squawk_proposer.py:220 - Placeholder comment found
  [placeholder] meeting_orchestrator_v1_DEPRECATED.py:320 - Placeholder comment found
  [placeholder] meeting_history_lookup.py:5 - Placeholder comment found
  [placeholder] risks_detector.py:19 - Placeholder comment found
  [placeholder] risks_detector.py:29 - Placeholder comment found
  [placeholder] list_integrator.py:20 - Placeholder comment found
  [placeholder] list_integrator.py:29 - Placeholder comment found
  [placeholder] list_integrator.py:31 - Placeholder comment found
  [placeholder] warm_intro_detector.py:19 - Placeholder comment found
  [placeholder] warm_intro_detector.py:29 - Placeholder comment found
  [placeholder] opportunities_detector.py:19 - Placeholder comment found
  [placeholder] opportunities_detector.py:29 - Placeholder comment found
  [placeholder] career_insights_generator.py:19 - Placeholder comment found
  [placeholder] career_insights_generator.py:27 - Placeholder comment found
  [placeholder] career_insights_generator.py:29 - Placeholder comment found
  [placeholder] email_history_fetcher.py:5 - Placeholder comment found
  [placeholder] competitive_intel_extractor.py:19 - Placeholder comment found
  [placeholder] competitive_intel_extractor.py:29 - Placeholder comment found
  [placeholder] user_research_extractor.py:19 - Placeholder comment found
  [placeholder] user_research_extractor.py:29 - Placeholder comment found
  [placeholder] stakeholder_classifier.py:242 - Placeholder comment found
  [placeholder] llm_client.py:63 - Placeholder comment found
  [placeholder] llm_client.py:79 - Placeholder comment found
  [placeholder] llm_client_real.py:40 - Placeholder comment found
  [placeholder] llm_client_real.py:51 - Placeholder comment found