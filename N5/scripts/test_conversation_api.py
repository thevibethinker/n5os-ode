#!/usr/bin/env python3
"""
Test AI-to-AI Conversation API
Validates all endpoints and conversation flow
"""

import json
import logging
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Run: pip install requests")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class ConversationAPITester:
    """Test suite for conversation API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.conversation_id: Optional[str] = None
        self.passed = 0
        self.failed = 0
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        logger.info("TEST: Health check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "ai-to-ai conversation" in data["features"]
            
            logger.info("✓ Health check passed")
            self.passed += 1
            return True
        
        except Exception as e:
            logger.error(f"✗ Health check failed: {e}")
            self.failed += 1
            return False
    
    def test_start_conversation(self) -> bool:
        """Test starting conversation"""
        logger.info("TEST: Start conversation")
        
        try:
            payload = {
                "initiator": "test_demonstrator",
                "context": {"phase": "test", "timestamp": time.time()}
            }
            
            response = requests.post(
                f"{self.base_url}/api/converse/start",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            assert "conversation_id" in data
            assert data["status"] == "started"
            
            self.conversation_id = data["conversation_id"]
            
            logger.info(f"✓ Conversation started: {self.conversation_id}")
            self.passed += 1
            return True
        
        except Exception as e:
            logger.error(f"✗ Start conversation failed: {e}")
            self.failed += 1
            return False
    
    def test_ask_question(self) -> bool:
        """Test asking question"""
        logger.info("TEST: Ask question")
        
        if not self.conversation_id:
            logger.error("✗ No conversation ID")
            self.failed += 1
            return False
        
        try:
            payload = {
                "conversation_id": self.conversation_id,
                "question": "What is the next step in bootstrap phase 2?",
                "metadata": {"test": True, "phase": "phase_2"}
            }
            
            response = requests.post(
                f"{self.base_url}/api/converse/ask",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            assert data["status"] == "received"
            
            logger.info("✓ Question asked successfully")
            self.passed += 1
            return True
        
        except Exception as e:
            logger.error(f"✗ Ask question failed: {e}")
            self.failed += 1
            return False
    
    def test_submit_response(self) -> bool:
        """Test parent submitting response"""
        logger.info("TEST: Submit response")
        
        if not self.conversation_id:
            logger.error("✗ No conversation ID")
            self.failed += 1
            return False
        
        try:
            payload = {
                "conversation_id": self.conversation_id,
                "answer": "The next step is to copy core scripts to the N5/scripts directory.",
                "metadata": {"test_response": True}
            }
            
            response = requests.post(
                f"{self.base_url}/api/converse/respond",
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            assert data["status"] == "queued"
            
            logger.info("✓ Response submitted successfully")
            self.passed += 1
            return True
        
        except Exception as e:
            logger.error(f"✗ Submit response failed: {e}")
            self.failed += 1
            return False
    
    def test_poll_response(self) -> bool:
        """Test polling for response"""
        logger.info("TEST: Poll for response")
        
        if not self.conversation_id:
            logger.error("✗ No conversation ID")
            self.failed += 1
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/converse/poll/{self.conversation_id}",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            assert data["conversation_id"] == self.conversation_id
            
            if data["status"] == "response_available":
                assert "response" in data
                logger.info(f"✓ Response retrieved: {data['response'][:50]}...")
                self.passed += 1
                return True
            elif data["status"] == "no_response":
                logger.info("✓ Poll successful (no response yet)")
                self.passed += 1
                return True
            else:
                raise ValueError(f"Unexpected status: {data['status']}")
        
        except Exception as e:
            logger.error(f"✗ Poll response failed: {e}")
            self.failed += 1
            return False
    
    def test_get_history(self) -> bool:
        """Test getting conversation history"""
        logger.info("TEST: Get history")
        
        if not self.conversation_id:
            logger.error("✗ No conversation ID")
            self.failed += 1
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/converse/history/{self.conversation_id}",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            assert "history" in data
            assert isinstance(data["history"], list)
            assert data["message_count"] > 0
            
            logger.info(f"✓ History retrieved: {data['message_count']} messages")
            self.passed += 1
            return True
        
        except Exception as e:
            logger.error(f"✗ Get history failed: {e}")
            self.failed += 1
            return False
    
    def test_full_conversation_flow(self) -> bool:
        """Test complete conversation flow"""
        logger.info("\nTEST: Full conversation flow")
        
        try:
            # 1. Start
            logger.info("Step 1: Start conversation")
            if not self.test_start_conversation():
                return False
            
            # 2. Ask question
            logger.info("Step 2: Ask question")
            if not self.test_ask_question():
                return False
            
            # 3. Submit response (simulating parent)
            logger.info("Step 3: Parent submits response")
            if not self.test_submit_response():
                return False
            
            # 4. Poll for response
            logger.info("Step 4: Poll for response")
            if not self.test_poll_response():
                return False
            
            # 5. Get history
            logger.info("Step 5: Get conversation history")
            if not self.test_get_history():
                return False
            
            logger.info("✓ Full conversation flow completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"✗ Full flow failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 60)
        logger.info("AI-to-AI Conversation API Test Suite")
        logger.info("=" * 60)
        
        # Basic health check
        self.test_health()
        
        # Full conversation flow
        self.test_full_conversation_flow()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            logger.info("\n🎉 All tests passed!")
            return 0
        else:
            logger.error(f"\n❌ {self.failed} test(s) failed")
            return 1


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test conversation API")
    parser.add_argument("--url", default="http://localhost:8769", help="Server URL")
    args = parser.parse_args()
    
    tester = ConversationAPITester(args.url)
    return tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
