import importlib.util
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "google_tasks_bridge.py"
spec = importlib.util.spec_from_file_location('google_tasks_bridge_under_test', MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class FakeGoogleTasksClient:
    def __init__(self, *args, **kwargs):
        self.updated = []
        self.created = []
        self.tasklists = {}
        self.tasks_by_list = {}
        self.next_task_id = 1

    def update_task(self, list_id, task_id, *, title, notes='', completed=False, due=None):
        payload = {
            'id': task_id,
            'list_id': list_id,
            'title': title,
            'notes': notes,
            'status': 'completed' if completed else 'needsAction',
            'completed': '2026-04-20T20:00:00Z' if completed else None,
            'due': due,
        }
        self.updated.append(payload)
        tasks = self.tasks_by_list.setdefault(list_id, [])
        for idx, item in enumerate(tasks):
            if item.get('id') == task_id:
                tasks[idx] = payload
                break
        else:
            tasks.append(payload)
        return payload

    def create_task(self, list_id, title, notes='', due=None):
        payload = {
            'id': f'receipt-{self.next_task_id}',
            'list_id': list_id,
            'title': title,
            'notes': notes,
            'status': 'needsAction',
            'due': due,
        }
        self.next_task_id += 1
        self.created.append(payload)
        self.tasks_by_list.setdefault(list_id, []).append(payload)
        return payload

    def list_tasklists(self, max_results=100):
        return list(self.tasklists.values())

    def list_tasks(self, list_id, updated_min=None, max_results=100):
        return list(self.tasks_by_list.get(list_id, []))

    def create_tasklist(self, title):
        list_id = f'list-{len(self.tasklists) + 1}'
        payload = {'id': list_id, 'title': title, 'updated': '2026-04-20T20:00:00Z'}
        self.tasklists[title] = payload
        self.tasks_by_list.setdefault(list_id, [])
        return payload


class BridgeBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / 'taskintake.db'
        bridge.initialize_db(self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _conn(self):
        return bridge.get_connection(self.db_path)

    def test_get_google_tasks_client_falls_back_to_token_store(self):
        token_path = Path(self.tmpdir.name) / 'token.json'
        token_path.write_text(
            json.dumps(
                {
                    "client_id": "client-from-file",
                    "client_secret": "secret-from-file",
                    "refresh_token": "refresh-from-file",
                    "scope": bridge.GOOGLE_TASKS_SCOPE,
                }
            )
        )
        old_path = bridge.GOOGLE_TASKS_TOKEN_PATH
        env_keys = (
            "GOOGLE_TASKS_CLIENT_ID",
            "GOOGLE_TASKS_CLIENT_SECRET",
            "GOOGLE_TASKS_REFRESH_TOKEN",
            "GOOGLE_TASKS_ACCESS_TOKEN",
            "GOOGLE_OAUTH_CLIENT_ID",
            "GOOGLE_OAUTH_CLIENT_SECRET",
            "GOOGLE_OAUTH_REFRESH_TOKEN",
        )
        old_env = {key: os.environ.get(key) for key in env_keys}
        try:
            bridge.GOOGLE_TASKS_TOKEN_PATH = token_path
            for key in old_env:
                os.environ.pop(key, None)
            creds = bridge.get_google_tasks_client()
        finally:
            bridge.GOOGLE_TASKS_TOKEN_PATH = old_path
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertEqual(creds, ("client-from-file", "secret-from-file", "refresh-from-file", None))

    def test_recover_stale_jobs_requeues_once_then_fails(self):
        with self._conn() as conn:
            conn.execute("INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)", ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'))
            conn.execute("INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?)", ('task-1', 'list-1', 'Draft intro @run', 'Draft intro', 'notes', 'needsAction', 'hash-1', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'))
            conn.execute("INSERT INTO execution_jobs (job_id, task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, retry_count, max_retries, attempt_token, lease_expires_at, worker_pid, writeback_done) VALUES (1, 'task-1', 'list-1', 'zo_worker', 'model', 'prompt', 'running', '2026-04-20T20:00:00Z', 0, 1, 'tok-1', '2000-01-01T00:00:00+00:00', 999999, 0)")
            conn.commit()
            first = bridge.recover_stale_jobs(conn)
            job = conn.execute("SELECT status, retry_count FROM execution_jobs WHERE job_id = 1").fetchone()
            self.assertEqual(first['requeued'], 1)
            self.assertEqual(job['status'], 'queued')
            self.assertEqual(job['retry_count'], 1)
            conn.execute("UPDATE execution_jobs SET status = 'running', attempt_token = 'tok-2', lease_expires_at = '2000-01-01T00:00:00+00:00', worker_pid = 999999 WHERE job_id = 1")
            conn.commit()
            second = bridge.recover_stale_jobs(conn)
            job = conn.execute("SELECT status FROM execution_jobs WHERE job_id = 1").fetchone()
            self.assertEqual(second['failed'], 1)
            self.assertEqual(job['status'], 'failed')

    def test_should_skip_writeback_when_already_completed(self):
        with self._conn() as conn:
            conn.execute("INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)", ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'))
            conn.execute("INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?)", ('task-1', 'list-1', 'Draft intro @run', 'Draft intro', 'notes', 'completed', 'hash-1', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'))
            conn.execute("INSERT INTO execution_jobs (job_id, task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, completed_at, response_json, writeback_done) VALUES (1, 'task-1', 'list-1', 'zo_worker', 'model', 'prompt', 'completed', '2026-04-20T20:00:00Z', '2026-04-20T20:05:00Z', '{\"ok\":true}', 1)")
            row = conn.execute("SELECT * FROM execution_jobs WHERE job_id = 1").fetchone()
            self.assertTrue(bridge.should_skip_writeback(row))

    def test_run_job_command_timeout_marks_failed(self):
        class TimeoutResponse:
            def __call__(self, *args, **kwargs):
                raise bridge.requests.Timeout('timed out')

        original_post = bridge.requests.post
        original_token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
        with self._conn() as conn:
            conn.execute("INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)", ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'))
            conn.execute("INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, due_date, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?)", ('task-1', 'list-1', 'Draft intro @run', 'Draft intro', 'Original notes', 'needsAction', None, 'hash-1', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'))
            conn.execute("INSERT INTO intake_candidates (task_id, list_id, canonical_title, execution_requested, action_type, functional_area, intent_class, parser_confidence, classifier_confidence, candidate_status, execution_target, last_routed_at, notes, classification_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ('task-1', 'list-1', 'Draft intro', 1, 'draft', 'communications', 'command', 0.9, 0.9, 'observed', 'zo_worker', '2026-04-20T20:00:00Z', 'Original notes', '{}'))
            conn.execute("INSERT INTO execution_jobs (job_id, task_id, list_id, execution_target, model_name, prompt_text, status, queued_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (1, 'task-1', 'list-1', 'zo_worker', 'model', 'prompt', 'queued', '2026-04-20T20:00:00Z'))
            conn.commit()
        try:
            bridge.requests.post = TimeoutResponse()
            os.environ['ZO_CLIENT_IDENTITY_TOKEN'] = 'dummy-token'
            bridge.run_job_command(SimpleNamespace(db=self.db_path, token_path=self.db_path, job_id=1, model='model'))
        finally:
            bridge.requests.post = original_post
            if original_token is None:
                os.environ.pop('ZO_CLIENT_IDENTITY_TOKEN', None)
            else:
                os.environ['ZO_CLIENT_IDENTITY_TOKEN'] = original_token
        with self._conn() as conn:
            job = conn.execute("SELECT status, error_text FROM execution_jobs WHERE job_id = 1").fetchone()
            self.assertEqual(job['status'], 'failed')
            self.assertIn('Timed out after', job['error_text'])

    def test_build_job_run_slug_prefers_primary_action_and_orderable_prefix(self):
        row = {
            'job_id': 13,
            'action_type': 'review',
            'normalized_title': "Review KIMS meeting report and send email to team",
            'notes': 'Email Anna and Shivam with the condensed report',
            'execution_target': 'zo_worker',
            'queued_at': '2026-04-20T21:27:15+00:00',
        }
        slug = bridge.build_job_run_slug(row)
        self.assertTrue(slug.startswith('013__send-email__'))
        self.assertIn('__zo-worker__2026-04-20T21-27-15Z', slug)

    def test_backfill_outputs_command_renames_legacy_directory(self):
        root = bridge.TASK_OUTPUTS_ROOT
        old_root = bridge.TASK_OUTPUTS_ROOT
        tmp_root = Path(self.tmpdir.name) / 'outputs'
        tmp_root.mkdir(parents=True, exist_ok=True)
        bridge.TASK_OUTPUTS_ROOT = tmp_root
        try:
            with self._conn() as conn:
                conn.execute("INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)", ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'))
                conn.execute("INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?)", ('task-13', 'list-1', 'Review KIMS report and send email @run', 'Review KIMS report and send email to team', 'Email team', 'completed', 'hash-13', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'))
                conn.execute("INSERT INTO intake_candidates (task_id, list_id, canonical_title, execution_requested, action_type, functional_area, intent_class, parser_confidence, classifier_confidence, candidate_status, execution_target, last_routed_at, notes, classification_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ('task-13', 'list-1', 'Review KIMS report and send email to team', 1, 'review', 'communications', 'command', 0.8, 0.8, 'observed', 'zo_worker', '2026-04-20T20:00:00Z', 'Email team', '{}'))
                conn.execute("INSERT INTO execution_jobs (job_id, task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, completed_at, response_json, writeback_done) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (13, 'task-13', 'list-1', 'zo_worker', 'model', 'prompt', 'completed', '2026-04-20T21:27:15+00:00', '2026-04-20T21:32:35+00:00', '{"summary":"done"}', 0))
                conn.commit()
            legacy = tmp_root / 'job-13-2026-04-20T21-27-15+00-00'
            legacy.mkdir()
            (legacy / 'TASK_STATUS.json').write_text('{"status":"completed"}')
            bridge.backfill_outputs_command(SimpleNamespace(db=self.db_path))
            dirs = [x.name for x in tmp_root.iterdir() if x.is_dir()]
            self.assertIn('013__send-email__email-to-team__zo-worker__2026-04-20T21-27-15Z', dirs)
        finally:
            bridge.TASK_OUTPUTS_ROOT = old_root

    def test_append_receipt_annotation_is_idempotent(self):
        annotation = '[Zo receipt]\njob_id: 9\ncompleted_at: 2026-04-20T20:00:00Z'
        first = bridge.append_receipt_annotation('Original notes', annotation)
        second = bridge.append_receipt_annotation(first, annotation)
        self.assertEqual(first, second)
        self.assertEqual(second.count('[Zo receipt]'), 1)

    def test_normalize_worker_output_preserves_dict_shape(self):
        raw = {
            'executed': 1,
            'summary': 'Prepared report',
            'actions_taken': ['Searched notes', 2],
            'remaining': ['Review with team'],
        }
        normalized = bridge.normalize_worker_output(raw)
        self.assertEqual(normalized['executed'], True)
        self.assertEqual(normalized['summary'], 'Prepared report')
        self.assertEqual(normalized['actions_taken'], ['Searched notes', '2'])
        self.assertEqual(normalized['remaining'], ['Review with team'])

    def test_normalize_worker_output_wraps_plain_text(self):
        normalized = bridge.normalize_worker_output('Plain text worker result')
        self.assertEqual(normalized['executed'], True)
        self.assertEqual(normalized['summary'], 'Plain text worker result')
        self.assertTrue(len(normalized['actions_taken']) >= 1)
        self.assertEqual(normalized['remaining'], [])

    def test_mark_google_task_processed_is_idempotent_for_receipt_task_by_job_id(self):
        client = FakeGoogleTasksClient()
        job = {
            'job_id': 12,
            'list_id': 'zo-commands-list',
            'task_id': 'task-12',
            'title': 'Draft intro @run',
            'normalized_title': 'Draft intro',
            'notes': 'Original notes',
            'due_date': None,
        }
        output = {
            'executed': True,
            'summary': 'Prepared intro copy for review.',
            'actions_taken': ['Drafted copy'],
            'remaining': [],
        }
        first = bridge.mark_google_task_processed(client, job, output, completed_at='2026-04-20T20:00:00Z')
        second = bridge.mark_google_task_processed(client, job, output, completed_at='2026-04-20T20:00:00Z')
        self.assertEqual(len(client.created), 1)
        self.assertEqual(first['receipt_task']['task_id'], second['receipt_task']['task_id'])

    def test_mark_google_task_processed_updates_original_and_creates_receipt(self):
        client = FakeGoogleTasksClient()
        job = {
            'job_id': 12,
            'list_id': 'zo-commands-list',
            'task_id': 'task-12',
            'title': 'Draft intro @run',
            'normalized_title': 'Draft intro',
            'notes': 'Original notes',
            'due_date': None,
        }
        output = {
            'executed': True,
            'summary': 'Prepared intro copy for review.',
            'actions_taken': ['Drafted copy'],
            'remaining': [],
        }

        result = bridge.mark_google_task_processed(client, job, output)

        self.assertEqual(len(client.updated), 1)
        self.assertEqual(len(client.created), 1)
        self.assertIn('[Zo receipt]', client.updated[0]['notes'])
        self.assertIn('job_id: 12', client.updated[0]['notes'])
        self.assertEqual(client.updated[0]['status'], 'completed')
        self.assertEqual(result['receipt_task']['list_title'], bridge.DEFAULT_RECEIPTS_LIST_TITLE)
        self.assertEqual(client.created[0]['title'], 'Processed: Draft intro')
        self.assertIn('[Zo receipt]', client.created[0]['notes'])

    def test_create_execution_job_cancels_duplicate_of_completed_equivalent(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)",
                ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'),
            )
            conn.execute(
                "INSERT INTO poll_runs (id, source_system, list_id, list_title, started_at, completed_at, status, fetched_count, changed_count, cursor_next) VALUES (1, 'google_tasks', 'list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z', 'complete', 2, 2, 'cursor-1')"
            )
            conn.execute(
                "INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at, last_run_id) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?, 1)",
                ('task-old', 'list-1', 'Draft intro @run', 'Draft intro', 'same notes', 'completed', 'hash-old', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'),
            )
            conn.execute(
                "INSERT INTO execution_jobs (task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, completed_at, response_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('task-old', 'list-1', 'zo_worker', 'model', 'prompt', 'completed', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z', '{}'),
            )
            conn.execute(
                "INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at, last_run_id) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?, 1)",
                ('task-new', 'list-1', 'Draft intro @run', 'Draft intro', 'same notes', 'needsAction', 'hash-new', '{}', '2026-04-20T20:02:00Z', '2026-04-20T20:02:00Z'),
            )
            conn.execute(
                "INSERT INTO intake_candidates (task_id, list_id, canonical_title, execution_requested, action_type, functional_area, intent_class, parser_confidence, classifier_confidence, candidate_status, execution_target, last_routed_at, notes, classification_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('task-new', 'list-1', 'Draft intro', 1, 'draft', 'communications', 'command', 0.9, 0.9, 'observed', 'zo_worker', '2026-04-20T20:02:00Z', 'same notes', '{}'),
            )
            task_row = conn.execute("SELECT * FROM google_tasks_current WHERE task_id = 'task-new'").fetchone()
            candidate = conn.execute("SELECT * FROM intake_candidates WHERE task_id = 'task-new'").fetchone()

            queued = bridge.create_execution_job(conn, task_row, candidate, 'model')
            conn.commit()

            self.assertFalse(queued)
            canceled = conn.execute("SELECT status, error_text FROM execution_jobs WHERE task_id = 'task-new'").fetchone()
            self.assertEqual(canceled['status'], 'canceled')
            self.assertIn('duplicate of completed equivalent job', canceled['error_text'])

    def test_upsert_inbound_task_recommits_existing_open_task_without_overwriting_older_due(self):
        client = FakeGoogleTasksClient()
        task_list = client.create_tasklist(bridge.DEFAULT_INBOUND_LIST_TITLE)
        existing_notes = bridge.render_inbound_notes({
            "canonical_key": "follow up with john",
            "confidence": 0.95,
            "source_events": [
                {
                    "event_key": "meeting:old:1",
                    "source_type": "meeting",
                    "source_id": "meeting-old",
                    "confidence": 0.95,
                    "summary": "Original commitment",
                    "due": "2026-05-01",
                }
            ],
            "recommit_count": 1,
            "linked_prior_completed_task_id": "",
            "due_status_note": "",
        })
        client.tasks_by_list[task_list["id"]] = [
            {
                "id": "task-open-1",
                "list_id": task_list["id"],
                "title": "Follow up with John",
                "notes": existing_notes,
                "status": "needsAction",
                "due": "2026-05-01",
            }
        ]

        result = bridge.upsert_inbound_task(
            client,
            title="Follow up with John",
            notes="Renewed commitment from latest meeting",
            due="2026-04-30",
            confidence=0.6,
            source_type="meeting",
            source_id="meeting-new",
            source_event_key="meeting:new:1",
            low_confidence_reason="Assignee 'All' is shared or ambiguous.",
            db_path=self.db_path,
        )

        self.assertEqual(result["action"], "updated_existing")
        self.assertEqual(len(client.updated), 1)
        self.assertEqual(client.updated[0]["due"], "2026-05-01")
        self.assertIn("Recommitted 2x.", client.updated[0]["notes"])
        self.assertIn("Due date preserved because incoming date was not newer and more specific.", client.updated[0]["notes"])
        self.assertIn("Low confidence capture (0.60)", client.updated[0]["notes"])

    def test_upsert_inbound_task_creates_new_linked_item_after_completed_equivalent(self):
        client = FakeGoogleTasksClient()
        task_list = client.create_tasklist(bridge.DEFAULT_INBOUND_LIST_TITLE)
        completed_notes = bridge.render_inbound_notes({
            "canonical_key": "draft intro email",
            "confidence": 0.95,
            "source_events": [
                {
                    "event_key": "meeting:older:1",
                    "source_type": "meeting",
                    "source_id": "meeting-older",
                    "confidence": 0.95,
                    "summary": "First commitment",
                    "due": None,
                },
                {
                    "event_key": "meeting:older:2",
                    "source_type": "meeting",
                    "source_id": "meeting-older-2",
                    "confidence": 0.95,
                    "summary": "Second commitment",
                    "due": None,
                },
            ],
            "recommit_count": 2,
            "linked_prior_completed_task_id": "",
            "due_status_note": "",
        })
        client.tasks_by_list[task_list["id"]] = [
            {
                "id": "task-done-1",
                "list_id": task_list["id"],
                "title": "Draft intro email",
                "notes": completed_notes,
                "status": "completed",
                "completed": "2026-04-20T20:00:00Z",
                "due": None,
            }
        ]

        result = bridge.upsert_inbound_task(
            client,
            title="Draft intro email",
            notes="Third commitment after previous completion",
            confidence=0.95,
            source_type="meeting",
            source_id="meeting-new",
            source_event_key="meeting:new:3",
            db_path=self.db_path,
        )

        self.assertEqual(result["action"], "created_linked_recommit")
        self.assertEqual(len(client.created), 1)
        self.assertIn("Recommitted 3x.", client.created[0]["notes"])
        self.assertIn("Linked prior completed equivalent: task-done-1", client.created[0]["notes"])

    def test_upsert_inbound_task_duplicate_event_is_noop(self):
        client = FakeGoogleTasksClient()
        task_list = client.create_tasklist(bridge.DEFAULT_INBOUND_LIST_TITLE)
        existing_notes = bridge.render_inbound_notes({
            "canonical_key": "follow up with john",
            "confidence": 0.95,
            "source_events": [
                {
                    "event_key": "meeting:new:1",
                    "source_type": "meeting",
                    "source_id": "meeting-new",
                    "confidence": 0.95,
                    "summary": "Original commitment",
                    "due": "2026-05-01",
                }
            ],
            "recommit_count": 1,
            "linked_prior_completed_task_id": "",
            "due_status_note": "",
        })
        client.tasks_by_list[task_list["id"]] = [
            {
                "id": "task-open-1",
                "list_id": task_list["id"],
                "title": "Follow up with John",
                "notes": existing_notes,
                "status": "needsAction",
                "due": "2026-05-01T00:00:00.000Z",
            }
        ]

        result = bridge.upsert_inbound_task(
            client,
            title="Follow up with John",
            notes="Duplicate source event",
            due="2026-05-01",
            confidence=0.95,
            source_type="meeting",
            source_id="meeting-new",
            source_event_key="meeting:new:1",
            db_path=self.db_path,
        )

        self.assertEqual(result["action"], "noop_existing_event")
        self.assertEqual(len(client.updated), 0)

    def test_sync_meeting_b05_to_inbound_filters_non_v_owned_items_and_marks_ambiguous(self):
        client = FakeGoogleTasksClient()
        meeting_dir = Path(self.tmpdir.name) / "2026-04-23_Test-Meeting"
        meeting_dir.mkdir(parents=True, exist_ok=True)
        (meeting_dir / "manifest.json").write_text(json.dumps({"meeting_id": "meeting-123"}))
        (meeting_dir / "B05_ACTION_ITEMS.md").write_text(
            "# B05\n\n"
            "- [ ] **<YOUR_NAME>**: Draft investor note\n"
            "- [ ] **All**: Confirm next steps\n"
            "- [ ] **John**: Send the deck\n"
        )

        result = bridge.sync_meeting_b05_to_inbound(meeting_dir, client=client, db_path=self.db_path)

        self.assertEqual(result["synced"], 2)
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(len(client.created), 2)
        self.assertTrue(any("Low confidence capture (0.60)" in item["notes"] for item in client.created))
        self.assertTrue(any(detail["status"] == "skipped" for detail in result["details"]))

    def test_parse_s02_v_owned_items_extracts_task_fields_and_relative_due(self):
        content = (
            "# ACTIONS\n\n"
            "## Decisions\n"
            "- Keep moving.\n\n"
            "## V-Owned Next Moves\n"
            "- `Task:` Send surgical clips to prospects. `Owner:` V. `Why V owns it:` V committed to send buyer-facing proof. "
            "`First step:` Cut the strongest 3 short clips and draft the message. `Deadline/check-in:` tomorrow.\n\n"
            "## Other-Owned Dependencies\n"
            "- Anna owes rig confirmation.\n\n"
            "## Open Items\n"
            "- None.\n"
        )

        items = bridge.parse_s02_v_owned_items(content, meeting_date="2026-04-20")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Send surgical clips to prospects")
        self.assertEqual(items[0]["due"], "2026-04-21")
        self.assertIn("Why V owns it: V committed to send buyer-facing proof.", items[0]["notes"])

    def test_sync_meeting_to_inbound_uses_s02_as_canonical_source(self):
        client = FakeGoogleTasksClient()
        meeting_dir = Path(self.tmpdir.name) / "2026-04-23_Test-S02"
        meeting_dir.mkdir(parents=True, exist_ok=True)
        (meeting_dir / "manifest.json").write_text(
            json.dumps({"meeting_id": "meeting-s02", "meeting": {"date": "2026-04-20"}})
        )
        (meeting_dir / "S02_ACTIONS.md").write_text(
            "# ACTIONS\n\n"
            "## Decisions\n"
            "- None.\n\n"
            "## V-Owned Next Moves\n"
            "- `Task:` Send surgical clips to prospects. `Owner:` V. `Why V owns it:` V committed to send clips. "
            "`First step:` Cut 3 short clips and send them. `Deadline/check-in:` tomorrow.\n\n"
            "## Other-Owned Dependencies\n"
            "- Geo owes the task list.\n\n"
            "## Open Items\n"
            "- None.\n"
        )
        (meeting_dir / "B05_ACTION_ITEMS.md").write_text(
            "# B05\n\n- [ ] **John**: Send the deck\n"
        )

        result = bridge.sync_meeting_to_inbound(meeting_dir, client=client, db_path=self.db_path)

        self.assertEqual(result["source_block"], "S02_ACTIONS.md")
        self.assertEqual(result["synced"], 1)
        self.assertEqual(len(client.created), 1)
        self.assertEqual(client.created[0]["title"], "Send surgical clips to prospects")
        self.assertEqual(client.created[0]["due"], "2026-04-21")
        self.assertIn("Source block: S02_ACTIONS.md", client.created[0]["notes"])

    def test_sync_meeting_to_inbound_does_not_fall_back_to_b05_when_s02_exists(self):
        client = FakeGoogleTasksClient()
        meeting_dir = Path(self.tmpdir.name) / "2026-04-23_Test-S02-Empty"
        meeting_dir.mkdir(parents=True, exist_ok=True)
        (meeting_dir / "manifest.json").write_text(
            json.dumps({"meeting_id": "meeting-s02-empty", "meeting": {"date": "2026-04-20"}})
        )
        (meeting_dir / "S02_ACTIONS.md").write_text(
            "# ACTIONS\n\n"
            "## Decisions\n"
            "- None.\n\n"
            "## V-Owned Next Moves\n"
            "No V-owned next moves identified.\n\n"
            "## Other-Owned Dependencies\n"
            "- Tyler owes the Loom.\n\n"
            "## Open Items\n"
            "- Wait for the Loom.\n"
        )
        (meeting_dir / "B05_ACTION_ITEMS.md").write_text(
            "# B05\n\n- [ ] **<YOUR_NAME>**: Review the Loom\n"
        )

        result = bridge.sync_meeting_to_inbound(meeting_dir, client=client, db_path=self.db_path)

        self.assertEqual(result["source_block"], "S02_ACTIONS.md")
        self.assertEqual(result["synced"], 0)
        self.assertEqual(len(client.created), 0)

    def test_collect_status_payload_and_human_report(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)",
                ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'),
            )
            conn.execute(
                "INSERT INTO poll_runs (id, source_system, list_id, list_title, started_at, completed_at, status, fetched_count, changed_count, cursor_next) VALUES (1, 'google_tasks', 'list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z', 'complete', 3, 2, 'cursor-1')"
            )
            conn.execute(
                "INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at, last_run_id) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?, 1)",
                ('task-1', 'list-1', 'Draft intro @run', 'Draft intro', 'notes', 'completed', 'hash-report', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'),
            )
            conn.execute(
                "INSERT INTO poll_runs (source_system, list_id, list_title, started_at, completed_at, status, fetched_count, changed_count, cursor_next) VALUES ('google_tasks', 'list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z', 'complete', 3, 2, 'cursor-1')"
            )
            conn.execute(
                "INSERT INTO execution_jobs (task_id, list_id, execution_target, model_name, prompt_text, status, queued_at, completed_at) VALUES ('task-1', 'list-1', 'zo_worker', 'model', 'prompt', 'completed', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z')"
            )
            payload = bridge.collect_status_payload(conn)

        self.assertEqual(payload['completed_jobs'], 1)
        self.assertEqual(payload['last_poll']['status'], 'complete')
        report = bridge.render_human_report(payload)
        self.assertIn('Google Tasks Bridge Report', report)
        self.assertIn('Last poll', report)
        self.assertIn('Last job', report)

    def test_report_command_defaults_human_readable(self):
        args = SimpleNamespace(db=self.db_path, json=False)
        from io import StringIO
        import contextlib

        with contextlib.redirect_stdout(StringIO()) as buffer:
            bridge.report_command(args)
        output = buffer.getvalue()
        self.assertIn('Google Tasks Bridge Report', output)

    def test_run_job_command_with_plain_text_worker_output(self):
        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {'output': 'Plain text worker result'}

        original_post = bridge.requests.post
        original_client_cls = bridge.GoogleTasksClient
        original_token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')

        with self._conn() as conn:
            conn.execute(
                "INSERT INTO google_task_lists (list_id, title, first_seen_at, last_seen_at, raw_json) VALUES (?, ?, ?, ?, ?)",
                ('list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z', '{}'),
            )
            conn.execute(
                "INSERT INTO poll_runs (id, source_system, list_id, list_title, started_at, completed_at, status, fetched_count, changed_count, cursor_next) VALUES (1, 'google_tasks', 'list-1', 'Zo Commands', '2026-04-20T20:00:00Z', '2026-04-20T20:01:00Z', 'complete', 1, 1, 'cursor-1')"
            )
            conn.execute(
                "INSERT INTO google_tasks_current (task_id, list_id, title, normalized_title, notes, status, due_date, deleted, hidden, execution_requested, snapshot_hash, raw_json, first_seen_at, last_seen_at, last_run_id) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 1, ?, ?, ?, ?, 1)",
                ('task-1', 'list-1', 'Draft intro @run', 'Draft intro', 'Original notes', 'needsAction', None, 'hash-1', '{}', '2026-04-20T20:00:00Z', '2026-04-20T20:00:00Z'),
            )
            conn.execute(
                "INSERT INTO intake_candidates (task_id, list_id, canonical_title, execution_requested, action_type, functional_area, intent_class, parser_confidence, classifier_confidence, candidate_status, execution_target, last_routed_at, notes, classification_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('task-1', 'list-1', 'Draft intro', 1, 'draft', 'communications', 'command', 0.9, 0.9, 'observed', 'zo_worker', '2026-04-20T20:00:00Z', 'Original notes', '{}'),
            )
            conn.execute(
                "INSERT INTO execution_jobs (job_id, task_id, list_id, execution_target, model_name, prompt_text, status, queued_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, 'task-1', 'list-1', 'zo_worker', 'model', 'prompt', 'queued', '2026-04-20T20:00:00Z'),
            )
            conn.commit()

        try:
            bridge.requests.post = lambda *args, **kwargs: FakeResponse()
            bridge.GoogleTasksClient = FakeGoogleTasksClient
            os.environ['ZO_CLIENT_IDENTITY_TOKEN'] = 'dummy-token'
            bridge.run_job_command(SimpleNamespace(db=self.db_path, token_path=self.db_path, job_id=1, model='model'))
        finally:
            bridge.requests.post = original_post
            bridge.GoogleTasksClient = original_client_cls
            if original_token is None:
                os.environ.pop('ZO_CLIENT_IDENTITY_TOKEN', None)
            else:
                os.environ['ZO_CLIENT_IDENTITY_TOKEN'] = original_token

        with self._conn() as conn:
            job = conn.execute("SELECT status, response_json, error_text FROM execution_jobs WHERE job_id = 1").fetchone()
            self.assertEqual(job['status'], 'completed')
            self.assertIsNotNone(job['response_json'])
            self.assertIn('Plain text worker result', job['response_json'])
            self.assertIsNone(job['error_text'])


if __name__ == '__main__':
    unittest.main()
