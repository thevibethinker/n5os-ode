#!/usr/bin/env python3
"""
Test helpers for E2E processing tests.
Provides metrics checking, log validation, message publishing, and DLQ management.
"""
import json
import requests
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import uuid


class MetricsChecker:
    """Check Prometheus metrics from consumer service."""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.baseline: Dict[str, float] = {}
        
    def reset_baseline(self):
        """Capture current metrics as baseline."""
        self.baseline = self._fetch_all()
        
    def get_delta(self, metric_name: str) -> float:
        """Get change in metric since baseline."""
        current = self._fetch_all()
        baseline_val = self.baseline.get(metric_name, 0)
        current_val = current.get(metric_name, 0)
        return current_val - baseline_val
    
    def _fetch_all(self) -> Dict[str, float]:
        """Fetch all metrics from endpoint."""
        try:
            resp = requests.get(self.endpoint, timeout=5)
            resp.raise_for_status()
            
            metrics = {}
            for line in resp.text.split('\n'):
                if line.startswith('#') or not line.strip():
                    continue
                
                # Simple parser: metric_name value
                parts = line.split()
                if len(parts) >= 2:
                    metric_name = parts[0]
                    try:
                        value = float(parts[1])
                        metrics[metric_name] = value
                    except ValueError:
                        continue
                        
            return metrics
        except Exception as e:
            print(f"Warning: Failed to fetch metrics: {e}")
            return {}


class LogValidator:
    """Validate structured JSON logs from consumer service."""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.logs: List[Dict[str, Any]] = []
        
    def clear(self):
        """Clear loaded logs."""
        self.logs = []
        
    def reload(self):
        """Reload logs from file."""
        self.clear()
        
        if not self.log_file.exists():
            return
            
        with open(self.log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    log_entry = json.loads(line)
                    self.logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
    
    def contains_event(self, event: str, **filters) -> bool:
        """Check if logs contain event matching filters."""
        self.reload()
        return self.find_event(event, **filters) is not None
    
    def find_event(self, event: str, **filters) -> Optional[Dict[str, Any]]:
        """Find first log entry matching event and filters."""
        self.reload()
        
        for log in self.logs:
            if log.get("event") != event:
                continue
                
            match = True
            for key, value in filters.items():
                if log.get(key) != value:
                    match = False
                    break
                    
            if match:
                return log
                
        return None
    
    def filter_events(self, event: str, **filters) -> List[Dict[str, Any]]:
        """Find all log entries matching event and filters."""
        self.reload()
        
        results = []
        for log in self.logs:
            if log.get("event") != event:
                continue
                
            match = True
            for key, value in filters.items():
                if log.get(key) != value:
                    match = False
                    break
                    
            if match:
                results.append(log)
                
        return results


class MessagePublisher:
    """Publish messages to SQS queue."""
    
    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        
    def publish(self, message: Dict[str, Any], force_message_id: Optional[str] = None) -> str:
        """
        Publish message to queue.
        
        Args:
            message: Message payload
            force_message_id: Optional - use specific message ID (for duplicate testing)
            
        Returns:
            Message ID
        """
        msg_id = force_message_id or str(uuid.uuid4())
        
        # Add message_id to payload if not present
        if "message_id" not in message:
            message["message_id"] = msg_id
        
        # Use AWS CLI to send to localstack
        payload = json.dumps(message)
        
        cmd = [
            "aws", "sqs", "send-message",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.queue_url,
            "--message-body", payload,
            "--message-attributes", 
            f"message_id={{StringValue={msg_id},DataType=String}}"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return msg_id
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to publish message: {e.stderr}")
    
    def purge_all(self):
        """Purge all messages from queue."""
        cmd = [
            "aws", "sqs", "purge-queue",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.queue_url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Ignore errors (queue might be empty)


class DLQManager:
    """Manage dead-letter queue operations."""
    
    def __init__(self, dlq_url: str, main_queue_url: str):
        self.dlq_url = dlq_url
        self.main_queue_url = main_queue_url
        
    def count(self) -> int:
        """Count messages in DLQ."""
        cmd = [
            "aws", "sqs", "get-queue-attributes",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.dlq_url,
            "--attribute-names", "ApproximateNumberOfMessages"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            return int(data.get("Attributes", {}).get("ApproximateNumberOfMessages", 0))
        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
            return 0
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message from DLQ by message_id."""
        cmd = [
            "aws", "sqs", "receive-message",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.dlq_url,
            "--max-number-of-messages", "10",
            "--message-attribute-names", "All"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            for msg in data.get("Messages", []):
                body = json.loads(msg["Body"])
                if body.get("message_id") == message_id:
                    return {
                        "payload": body,
                        "metadata": msg.get("MessageAttributes", {}),
                        "receipt_handle": msg["ReceiptHandle"]
                    }
                    
            return None
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None
    
    def replay(self, message_id: str):
        """Replay message from DLQ to main queue."""
        dlq_msg = self.get_message(message_id)
        
        if not dlq_msg:
            raise ValueError(f"Message {message_id} not found in DLQ")
        
        # Publish to main queue
        publisher = MessagePublisher(self.main_queue_url)
        publisher.publish(dlq_msg["payload"], force_message_id=message_id)
        
        # Delete from DLQ
        cmd = [
            "aws", "sqs", "delete-message",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.dlq_url,
            "--receipt-handle", dlq_msg["receipt_handle"]
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def purge(self):
        """Purge all messages from DLQ."""
        cmd = [
            "aws", "sqs", "purge-queue",
            "--endpoint-url", "http://localhost:4566",
            "--queue-url", self.dlq_url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass


class ConsumerManager:
    """Manage consumer service lifecycle for testing."""
    
    def __init__(self, start_cmd: str, health_check_url: str):
        self.start_cmd = start_cmd
        self.health_check_url = health_check_url
        self.process: Optional[subprocess.Popen] = None
        
    def start(self):
        """Start consumer service."""
        if self.process and self.process.poll() is None:
            return  # Already running
        
        self.process = subprocess.Popen(
            self.start_cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for health check
        for _ in range(30):
            try:
                resp = requests.get(self.health_check_url, timeout=1)
                if resp.status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(1)
            
        raise RuntimeError("Consumer failed to start within 30s")
    
    def stop(self, graceful: bool = True):
        """Stop consumer service."""
        if not self.process or self.process.poll() is not None:
            return  # Not running
        
        if graceful:
            self.process.terminate()
            self.process.wait(timeout=10)
        else:
            self.process.kill()
            self.process.wait(timeout=5)
        
        self.process = None
    
    def restart(self, graceful: bool = True):
        """Restart consumer service."""
        self.stop(graceful=graceful)
        time.sleep(1)
        self.start()
