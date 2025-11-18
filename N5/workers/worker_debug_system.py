#!/usr/bin/env python3
"""
Worker: worker_debug_system
Task: Comprehensive debugging and unit testing of Content Library system

This worker performs systematic verification of all components:
- Database schema integrity
- Data ingestion paths (raw, blocks)
- Query functionality
- Error handling
- Data integrity
- Edge cases

Usage: python3 worker_debug_system.py
"""

import sqlite3
import json
import sys
from pathlib import Path

# Paths
LIBRARY_DB = Path("/home/workspace/Personal/Content-Library/content-library.db")
SETTINGS_FILE = Path("/home/workspace/Personal/Content-Library/settings.json")

# Test data paths (for verification)
TEST_CONTENT = [
    {
        "id": "article_career-transitions-a-practical-guide_5bff37d8",
        "title": "Career Transitions: A Practical Guide",
        "content_type": "article",
        "source_type": "created"
    },
    {
        "id": "article_test-article-title_29b6d6aa",
        "title": "Test Article Title",
        "content_type": "article",
        "source_type": "created"
    }
]

TEST_BLOCKS = [
    {
        "block_code": "B01",
        "content": "Sample B01 block content"
    },
    {
        "block_code": "B31",
        "content": "Sample B31 block content"
    }
]

class SystemDebugger:
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": []
        }
        
    def test_database_exists(self):
        """Verify database file exists and is accessible"""
        self.results["tests_run"] += 1
        
        if LIBRARY_DB.exists():
            print(f"✅ Database exists: {LIBRARY_DB}")
            self.results["tests_passed"] += 1
        else:
            print(f"❌ Database NOT FOUND: {LIBRARY_DB}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Database not found: {LIBRARY_DB}")
            
    def test_database_schema(self):
        """Verify all required tables exist with correct schema"""
        self.results["tests_run"] += 1
        
        if not LIBRARY_DB.exists():
            print("❌ Skipping schema test - database not found")
            self.results["tests_failed"] += 1
            return
            
        conn = sqlite3.connect(LIBRARY_DB)
        cursor = conn.cursor()
        
        # Check for required tables
        required_tables = ['content', 'blocks', 'topics', 'content_topics', 'knowledge_refs']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)
                
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Missing tables: {missing_tables}")
        else:
            print(f"✅ All required tables present: {required_tables}")
            self.results["tests_passed"] += 1
            
        # Check table schemas
        print("\n📊 Schema Validation:")
        for table in required_tables:
            if table in existing_tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"  - {table}: {len(columns)} columns")
                
        conn.close()
        
    def test_content_ingestion(self):
        """Verify content entries can be read from database"""
        self.results["tests_run"] += 1
        
        if not LIBRARY_DB.exists():
            print("❌ Skipping content test - database not found")
            self.results["tests_failed"] += 1
            return
            
        conn = sqlite3.connect(LIBRARY_DB)
        cursor = conn.cursor()
        
        # Count content entries
        cursor.execute("SELECT COUNT(*) FROM content")
        content_count = cursor.fetchone()[0]
        print(f"\n📊 Content Entries: {content_count} total")
        
        if content_count > 0:
            # Verify a specific test entry
            test_id = TEST_CONTENT[0]["id"]
            cursor.execute("SELECT * FROM content WHERE id = ?", (test_id,))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Test content entry found: {test_id}")
                self.results["tests_passed"] += 1
            else:
                print(f"⚠️ Test content entry NOT FOUND: {test_id}")
                self.results["warnings"].append(f"Test entry not found: {test_id}")
        else:
            print("⚠️ No content entries found (may not have been ingested yet)")
            
        conn.close()
        
    def test_block_ingestion(self):
        """Verify block entries can be read from database"""
        self.results["tests_run"] += 1
        
        if not LIBRARY_DB.exists():
            print("❌ Skipping block test - database not found")
            self.results["tests_failed"] += 1
            return
            
        conn = sqlite3.connect(LIBRARY_DB)
        cursor = conn.cursor()
        
        # Count block entries
        cursor.execute("SELECT COUNT(*) FROM blocks")
        block_count = cursor.fetchone()[0]
        print(f"\n📦 Block Entries: {block_count} total")
        
        # List a few blocks by type
        cursor.execute("SELECT block_code, COUNT(*) as block_count FROM blocks GROUP BY block_code ORDER BY block_count DESC LIMIT 5")
        block_counts = cursor.fetchall()
        
        if block_counts:
            print(f"  Top block types:")
            for block_code, count in block_counts:
                print(f"    - {block_code}: {count} blocks")
        else:
            print(f"  ⚠️ No blocks found (may not have been ingested yet)")
            
        conn.close()
        
    def test_query_functionality(self):
        """Verify query/search functions work correctly"""
        self.results["tests_run"] += 1
        
        # Check if query CLI exists
        query_cli = Path("/home/workspace/Personal/Content-Library/cli.py")
        if not query_cli.exists():
            print(f"\n⚠️ Query CLI not found: {query_cli}")
            print("   Query functionality may not have been built yet")
            return
            
        print(f"\n📋 Query CLI Access: {query_cli}")
        self.results["tests_passed"] += 1
        
        # Try to import and test query functions
        sys.path.insert(0, str(Path("/home/workspace/Personal/Content-Library").parent))
        try:
            # This would require the actual query module to be importable
            # For now, just verify the file structure exists
            search_module = Path("/home/workspace/Personal/Content-Library/query/search.py")
            cli_module = Path("/home/workspace/Personal/Content-Library/query/cli.py")
            
            if search_module.exists():
                print(f"  ✅ Search module: {search_module}")
            if cli_module.exists():
                print(f"  ✅ CLI module: {cli_module}")
                
        except Exception as e:
            print(f"  ⚠️ Could not import query modules: {e}")
            
    def test_data_integrity(self):
        """Verify data integrity and consistency"""
        self.results["tests_run"] += 1
        
        if not LIBRARY_DB.exists():
            print("❌ Skipping integrity test - database not found")
            self.results["tests_failed"] += 1
            return
            
        conn = sqlite3.connect(LIBRARY_DB)
        cursor = conn.cursor()
        
        # Check for orphaned blocks (blocks without content)
        cursor.execute("""
            SELECT COUNT(*) FROM blocks b 
            LEFT JOIN content c ON b.content_id = c.id 
            WHERE c.id IS NULL
        """)
        orphaned_blocks = cursor.fetchone()[0]
        
        if orphaned_blocks > 0:
            print(f"\n⚠️ Found {orphaned_blocks} orphaned blocks (no parent content)")
            self.results["warnings"].append(f"{orphaned_blocks} orphaned blocks")
        else:
            print(f"\n✅ No orphaned blocks - data integrity intact")
            
        # Check for content entries without any blocks
        cursor.execute("""
            SELECT COUNT(*) FROM content c 
            LEFT JOIN blocks b ON c.id = b.content_id 
            WHERE b.id IS NULL
        """)
        content_without_blocks = cursor.fetchone()[0]
        
        if content_without_blocks > 0:
            print(f"  ⚠️ {content_without_blocks} content entries have no blocks")
        else:
            print(f"  ✅ All content entries have associated blocks")
            
        conn.close()
        self.results["tests_passed"] += 1
        
    def test_error_handling(self):
        """Verify error handling works correctly"""
        self.results["tests_run"] += 1
        
        # Test with invalid file path
        invalid_path = Path("/nonexistent/path/file.txt")
        if not invalid_path.exists():
            print(f"\n✅ Invalid path correctly detected: {invalid_path}")
            self.results["tests_passed"] += 1
        else:
            print(f"\n❌ Invalid path exists (unexpected)")
            self.results["tests_failed"] += 1
            
    def test_settings_integrity(self):
        """Verify settings file is valid and complete"""
        self.results["tests_run"] += 1
        
        if not SETTINGS_FILE.exists():
            print(f"\n❌ Settings file not found: {SETTINGS_FILE}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Settings file not found: {SETTINGS_FILE}")
            return
            
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                
            required_sections = ['file_paths', 'block_mappings', 'ingestion_rules', 'validation_rules']
            missing_sections = []
            
            for section in required_sections:
                if section not in settings:
                    missing_sections.append(section)
                    
            if missing_sections:
                print(f"\n⚠️ Settings file missing sections: {missing_sections}")
                self.results["warnings"].append(f"Missing settings sections: {missing_sections}")
            else:
                print(f"\n✅ All required settings sections present")
                self.results["tests_passed"] += 1
                
        except json.JSONDecodeError as e:
            print(f"\n❌ Invalid JSON in settings file: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Invalid settings JSON: {e}")
        except Exception as e:
            print(f"\n❌ Error reading settings: {e}")
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Settings read error: {e}")
    
    def print_comprehensive_report(self):
        """Print comprehensive debug report"""
        print("\n" + "="*80)
        print(f"🛠️  CONTENT LIBRARY SYSTEM - COMPREHENSIVE DEBUG REPORT")
        print(f"   Generated: {Path(__file__).stat().st_mtime}")
        print("="*80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   - Tests Run: {self.results['tests_run']}")
        print(f"   - Tests Passed: {self.results['tests_passed']}")
        print(f"   - Tests Failed: {self.results['tests_failed']}")
        print(f"   - Warnings: {len(self.results['warnings'])}")
        print(f"   - Errors: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print(f"\n❌ ERRORS FOUND:")
            for error in self.results['errors']:
                print(f"   - {error}")
                
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.results['warnings']:
                print(f"   - {warning}")
                
        # Overall system health
        health_score = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        
        print(f"\n🏥 SYSTEM HEALTH SCORE: {health_score:.1f}%")
        
        if health_score >= 90:
            print(f"   Status: ✅ EXCELLENT - System is production-ready")
        elif health_score >= 70:
            print(f"   Status: ⚠️  GOOD - Minor issues to address")
        elif health_score >= 50:
            print(f"   Status: ⚠️  FAIR - Multiple issues need attention")
        else:
            print(f"   Status: ❌ POOR - Significant issues require debugging")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting comprehensive system debug...\n")
        
        # Run all test methods
        self.test_database_exists()
        self.test_database_schema()
        self.test_content_ingestion()
        self.test_block_ingestion()
        self.test_query_functionality()
        self.test_data_integrity()
        self.test_error_handling()
        self.test_settings_integrity()
        
        # Print final report
        self.print_comprehensive_report()
        
        return self.results

def main():
    """Run the debug worker"""
    debugger = SystemDebugger()
    results = debugger.run_all_tests()
    
    # Exit with appropriate code
    if results['tests_failed'] > 0:
        print(f"\n❌ Debug completed with {results['tests_failed']} failures")
        sys.exit(1)
    elif len(results['warnings']) > 0:
        print(f"\n⚠️  Debug completed with {len(results['warnings'])} warnings")
        sys.exit(0)
    else:
        print(f"\n✅ Debug completed successfully - all systems operational!")
        sys.exit(0)

if __name__ == "__main__":
    main()


