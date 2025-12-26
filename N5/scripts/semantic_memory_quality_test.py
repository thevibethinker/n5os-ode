#!/usr/bin/env python3
"""
N5 Semantic Memory Quality Assessment Suite
============================================
Tests retrieval quality, embedding coherence, chunking quality, 
coverage validation, and hybrid search comparison.

Author: Worker OZSS3k9igDENRq9E
Date: 2025-12-12
"""

import sys
import os
import sqlite3
import json
import logging
import re
import datetime
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# Add the cognition directory to path
sys.path.insert(0, "/home/workspace/N5/cognition")
from n5_memory_client import N5MemoryClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
LOG = logging.getLogger("semantic_quality_test")

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestResult:
    """Single test result"""
    test_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: str
    examples: List[Dict] = field(default_factory=list)

@dataclass
class QualityReport:
    """Aggregate quality report"""
    generated_at: str
    db_stats: Dict[str, int]
    retrieval_quality: Dict[str, Any]
    embedding_coherence: Dict[str, Any]
    chunking_quality: Dict[str, Any]
    coverage_validation: Dict[str, Any]
    hybrid_vs_semantic: Dict[str, Any]
    overall_score: float
    recommendations: List[str]

# ============================================================================
# TEST CASES - Domain-Specific Query/Expected Pairs
# ============================================================================

RETRIEVAL_TEST_CASES = [
    {
        "name": "Careerspan company query",
        "query": "What is Careerspan and what does the company do?",
        "expected_paths": ["Careerspan", "careerspan"],
        "expected_keywords": ["career", "talent", "job", "hiring"],
        "description": "Should retrieve Careerspan-related documents"
    },
    {
        "name": "Meeting system architecture",
        "query": "How does the meeting processing system work in N5?",
        "expected_paths": ["meeting", "Meeting", "MEETING"],
        "expected_keywords": ["meeting", "transcript", "process", "pipeline"],
        "description": "Should retrieve meeting system docs"
    },
    {
        "name": "CRM functionality",
        "query": "How to add contacts to the CRM system?",
        "expected_paths": ["CRM", "crm"],
        "expected_keywords": ["contact", "profile", "crm", "relationship"],
        "description": "Should retrieve CRM-related documentation"
    },
    {
        "name": "Warm intro generator",
        "query": "Generate warm introductions for networking",
        "expected_paths": ["warm", "intro", "Warm", "Intro"],
        "expected_keywords": ["intro", "warm", "networking", "connection"],
        "description": "Should retrieve warm intro related files"
    },
    {
        "name": "Knowledge management",
        "query": "How to store and retrieve knowledge in N5?",
        "expected_paths": ["knowledge", "Knowledge"],
        "expected_keywords": ["knowledge", "ingest", "store", "retrieval"],
        "description": "Should retrieve knowledge system docs"
    },
    {
        "name": "Embedding and vector search",
        "query": "semantic search embedding vectors RAG",
        "expected_paths": ["memory", "embed", "vector", "cognition"],
        "expected_keywords": ["embedding", "vector", "semantic", "search"],
        "description": "Should retrieve RAG/embedding docs"
    },
    {
        "name": "Persona and routing",
        "query": "Vibe personas and how routing works",
        "expected_paths": ["persona", "Persona", "routing"],
        "expected_keywords": ["persona", "vibe", "operator", "routing"],
        "description": "Should retrieve persona system docs"
    },
    {
        "name": "Scheduled tasks agents",
        "query": "How do scheduled tasks and agents work?",
        "expected_paths": ["schedule", "agent", "task"],
        "expected_keywords": ["schedule", "agent", "task", "automated"],
        "description": "Should retrieve scheduling documentation"
    }
]

# Document pairs that should be semantically similar
SIMILARITY_TEST_PAIRS = [
    {
        "name": "CRM profiles similarity",
        "path1_pattern": "%crm/individuals/aaron%",
        "path2_pattern": "%crm/individuals/adam%",
        "expected_similarity": 0.5,  # Should be moderately similar (both are people profiles)
        "description": "Two CRM individual profiles should have some similarity"
    },
    {
        "name": "Meeting docs similarity",
        "path1_pattern": "%meeting-process%",
        "path2_pattern": "%meeting-system%",
        "expected_similarity": 0.6,
        "description": "Meeting-related docs should be similar"
    },
    {
        "name": "Knowledge ingest docs",
        "path1_pattern": "%knowledge-ingest%",
        "path2_pattern": "%knowledge-add%",
        "expected_similarity": 0.5,
        "description": "Knowledge management docs should be similar"
    }
]

# Critical files that MUST be indexed
CRITICAL_FILES = [
    "/home/workspace/N5/README.md",
    "/home/workspace/N5/prefs/prefs.md",
    "/home/workspace/Knowledge/README.md",
    "/home/workspace/Documents/System/README.md",
    "/home/workspace/N5/docs/system_guide_v2.md",
]

# ============================================================================
# TEST IMPLEMENTATION
# ============================================================================

class SemanticMemoryQualityTester:
    def __init__(self, db_path: str = "/home/workspace/N5/cognition/brain.db"):
        self.db_path = db_path
        self.client = N5MemoryClient(db_path=db_path)
        self.conn = sqlite3.connect(db_path)
        self.results: List[TestResult] = []
        
    def get_db_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM resources")
        stats["total_resources"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM blocks")
        stats["total_blocks"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vectors")
        stats["total_vectors"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(LENGTH(content)) FROM blocks")
        stats["avg_chunk_size"] = int(cursor.fetchone()[0] or 0)
        
        cursor.execute("SELECT MIN(LENGTH(content)), MAX(LENGTH(content)) FROM blocks")
        row = cursor.fetchone()
        stats["min_chunk_size"] = row[0] or 0
        stats["max_chunk_size"] = row[1] or 0
        
        return stats
    
    # =========================================================================
    # TEST 1: RETRIEVAL QUALITY
    # =========================================================================
    
    def test_retrieval_quality(self) -> Dict[str, Any]:
        """Test if queries return relevant documents"""
        LOG.info("Testing retrieval quality...")
        
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "average_precision": 0.0,
            "average_recall": 0.0,
            "individual_results": []
        }
        
        total_precision = 0.0
        total_recall = 0.0
        
        for test_case in RETRIEVAL_TEST_CASES:
            LOG.info(f"  Testing: {test_case['name']}")
            
            # Run search
            search_results = self.client.search(
                query=test_case["query"],
                limit=10,
                use_hybrid=True
            )
            
            # Calculate metrics
            retrieved_paths = [r.get("path", "") for r in search_results]
            
            # Check path matches
            path_matches = 0
            for path in retrieved_paths:
                for expected in test_case["expected_paths"]:
                    if expected.lower() in path.lower():
                        path_matches += 1
                        break
            
            # Check keyword matches in content
            keyword_matches = 0
            total_keywords = len(test_case["expected_keywords"])
            for result in search_results:
                content = result.get("content", "").lower()
                for keyword in test_case["expected_keywords"]:
                    if keyword.lower() in content:
                        keyword_matches += 1
                        break
            
            # Calculate precision (relevant in top K / K)
            precision = path_matches / len(search_results) if search_results else 0
            
            # Calculate recall proxy (did we get at least some relevant results?)
            recall = min(1.0, path_matches / 3) if path_matches > 0 else 0  # Expect at least 3 relevant
            
            passed = precision >= 0.3 and path_matches >= 2
            
            test_result = {
                "name": test_case["name"],
                "query": test_case["query"],
                "passed": passed,
                "precision": round(precision, 3),
                "recall_proxy": round(recall, 3),
                "path_matches": path_matches,
                "keyword_matches": keyword_matches,
                "top_results": [
                    {"path": r.get("path", "")[:80], "score": round(r.get("score", 0), 4)}
                    for r in search_results[:5]
                ]
            }
            
            results["individual_results"].append(test_result)
            results["tests_run"] += 1
            if passed:
                results["tests_passed"] += 1
            
            total_precision += precision
            total_recall += recall
        
        results["average_precision"] = round(total_precision / len(RETRIEVAL_TEST_CASES), 3)
        results["average_recall"] = round(total_recall / len(RETRIEVAL_TEST_CASES), 3)
        results["overall_score"] = round(results["tests_passed"] / results["tests_run"], 3)
        
        return results
    
    # =========================================================================
    # TEST 2: EMBEDDING COHERENCE
    # =========================================================================
    
    def test_embedding_coherence(self) -> Dict[str, Any]:
        """Test if semantically similar documents are close in vector space"""
        LOG.info("Testing embedding coherence...")
        
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "average_similarity": 0.0,
            "individual_results": []
        }
        
        total_similarity = 0.0
        cursor = self.conn.cursor()
        
        for test_pair in SIMILARITY_TEST_PAIRS:
            LOG.info(f"  Testing: {test_pair['name']}")
            
            # Get embedding for first document
            cursor.execute("""
                SELECT v.embedding, r.path 
                FROM vectors v 
                JOIN blocks b ON v.block_id = b.id 
                JOIN resources r ON b.resource_id = r.id 
                WHERE r.path LIKE ? 
                LIMIT 1
            """, (test_pair["path1_pattern"],))
            row1 = cursor.fetchone()
            
            cursor.execute("""
                SELECT v.embedding, r.path 
                FROM vectors v 
                JOIN blocks b ON v.block_id = b.id 
                JOIN resources r ON b.resource_id = r.id 
                WHERE r.path LIKE ? 
                LIMIT 1
            """, (test_pair["path2_pattern"],))
            row2 = cursor.fetchone()
            
            if row1 and row2:
                vec1 = np.frombuffer(row1[0], dtype=np.float32)
                vec2 = np.frombuffer(row2[0], dtype=np.float32)
                
                # Cosine similarity
                similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-9)
                similarity = float(similarity)
                
                passed = similarity >= test_pair["expected_similarity"] * 0.7  # 70% of expected
                
                test_result = {
                    "name": test_pair["name"],
                    "path1": row1[1][:60],
                    "path2": row2[1][:60],
                    "similarity": round(similarity, 4),
                    "expected_min": test_pair["expected_similarity"],
                    "passed": passed
                }
                
                total_similarity += similarity
                results["tests_run"] += 1
                if passed:
                    results["tests_passed"] += 1
            else:
                test_result = {
                    "name": test_pair["name"],
                    "path1": test_pair["path1_pattern"],
                    "path2": test_pair["path2_pattern"],
                    "similarity": 0,
                    "error": "One or both documents not found",
                    "passed": False
                }
                results["tests_run"] += 1
            
            results["individual_results"].append(test_result)
        
        if results["tests_run"] > 0:
            results["average_similarity"] = round(total_similarity / results["tests_run"], 3)
            results["overall_score"] = round(results["tests_passed"] / results["tests_run"], 3)
        
        # Additional: check self-similarity (same doc chunks should be very similar)
        LOG.info("  Testing self-similarity of chunks from same document...")
        cursor.execute("""
            SELECT v.embedding, b.resource_id, r.path
            FROM vectors v
            JOIN blocks b ON v.block_id = b.id
            JOIN resources r ON b.resource_id = r.id
            WHERE b.resource_id IN (
                SELECT resource_id FROM blocks GROUP BY resource_id HAVING COUNT(*) >= 3
            )
            LIMIT 100
        """)
        
        embeddings_by_resource = defaultdict(list)
        paths_by_resource = {}
        for row in cursor.fetchall():
            emb = np.frombuffer(row[0], dtype=np.float32)
            embeddings_by_resource[row[1]].append(emb)
            paths_by_resource[row[1]] = row[2]
        
        self_similarities = []
        for resource_id, embs in embeddings_by_resource.items():
            if len(embs) >= 2:
                sim = np.dot(embs[0], embs[1]) / (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1]) + 1e-9)
                self_similarities.append(float(sim))
        
        if self_similarities:
            results["self_similarity_avg"] = round(np.mean(self_similarities), 3)
            results["self_similarity_min"] = round(np.min(self_similarities), 3)
            results["self_similarity_max"] = round(np.max(self_similarities), 3)
        
        return results
    
    # =========================================================================
    # TEST 3: CHUNKING QUALITY
    # =========================================================================
    
    def test_chunking_quality(self) -> Dict[str, Any]:
        """Test if chunks are well-formed (no truncations, good boundaries)"""
        LOG.info("Testing chunking quality...")
        
        results = {
            "total_chunks_analyzed": 0,
            "truncated_sentences": 0,
            "broken_markdown": 0,
            "orphan_headers": 0,
            "ideal_size_chunks": 0,
            "too_small_chunks": 0,
            "too_large_chunks": 0,
            "examples_bad": [],
            "examples_good": []
        }
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT b.content, b.id, r.path 
            FROM blocks b 
            JOIN resources r ON b.resource_id = r.id
            LIMIT 500
        """)
        
        for row in cursor.fetchall():
            content, block_id, path = row
            results["total_chunks_analyzed"] += 1
            
            issues = []
            
            # Check for truncated sentences (ends mid-word or mid-sentence)
            content_stripped = content.strip()
            if content_stripped and not content_stripped[-1] in '.!?"\'\n`':
                # Might be truncated - check if it looks like mid-sentence
                last_words = content_stripped.split()[-3:] if len(content_stripped.split()) >= 3 else []
                if last_words and not any(w.endswith(('.', '!', '?', ':', '"', "'", '`', '-')) for w in last_words):
                    results["truncated_sentences"] += 1
                    issues.append("truncated_sentence")
            
            # Check for broken markdown (unclosed code blocks)
            code_block_opens = content.count('```')
            if code_block_opens % 2 != 0:
                results["broken_markdown"] += 1
                issues.append("unclosed_code_block")
            
            # Check for orphan headers (header at end with no content)
            lines = content.strip().split('\n')
            if lines and re.match(r'^#{1,6}\s', lines[-1]):
                results["orphan_headers"] += 1
                issues.append("orphan_header")
            
            # Check chunk size
            chunk_len = len(content)
            if 200 <= chunk_len <= 2000:
                results["ideal_size_chunks"] += 1
            elif chunk_len < 100:
                results["too_small_chunks"] += 1
                issues.append("too_small")
            elif chunk_len > 3000:
                results["too_large_chunks"] += 1
                issues.append("too_large")
            
            # Store examples
            if issues and len(results["examples_bad"]) < 5:
                results["examples_bad"].append({
                    "path": path[:60],
                    "block_id": block_id,
                    "issues": issues,
                    "preview": content[:150] + "..." if len(content) > 150 else content,
                    "ending": content[-50:] if len(content) > 50 else content
                })
            elif not issues and len(results["examples_good"]) < 3:
                results["examples_good"].append({
                    "path": path[:60],
                    "block_id": block_id,
                    "size": chunk_len,
                    "preview": content[:100] + "..."
                })
        
        # Calculate quality score
        total = results["total_chunks_analyzed"]
        if total > 0:
            issues_count = (results["truncated_sentences"] + 
                          results["broken_markdown"] + 
                          results["orphan_headers"] +
                          results["too_small_chunks"] +
                          results["too_large_chunks"])
            results["quality_score"] = round(1 - (issues_count / total), 3)
            results["issues_percentage"] = round(issues_count / total * 100, 1)
        else:
            results["quality_score"] = 0
            results["issues_percentage"] = 100
        
        return results
    
    # =========================================================================
    # TEST 4: COVERAGE VALIDATION
    # =========================================================================
    
    def test_coverage_validation(self) -> Dict[str, Any]:
        """Test if critical files are indexed"""
        LOG.info("Testing coverage validation...")
        
        results = {
            "critical_files_checked": len(CRITICAL_FILES),
            "critical_files_indexed": 0,
            "missing_critical": [],
            "present_critical": [],
            "directory_coverage": {}
        }
        
        cursor = self.conn.cursor()
        
        # Check critical files
        for file_path in CRITICAL_FILES:
            cursor.execute("SELECT id, hash FROM resources WHERE path = ?", (file_path,))
            row = cursor.fetchone()
            if row:
                results["critical_files_indexed"] += 1
                results["present_critical"].append(file_path)
            else:
                results["missing_critical"].append(file_path)
        
        # Check directory coverage
        important_dirs = [
            "/home/workspace/N5/",
            "/home/workspace/Knowledge/",
            "/home/workspace/Documents/",
            "/home/workspace/Personal/",
            "/home/workspace/Prompts/",
        ]
        
        for dir_path in important_dirs:
            # Count files in filesystem
            dir_name = dir_path.rstrip('/').split('/')[-1]
            
            # Count indexed files from this directory
            cursor.execute(
                "SELECT COUNT(*) FROM resources WHERE path LIKE ?",
                (f"{dir_path}%",)
            )
            indexed_count = cursor.fetchone()[0]
            
            results["directory_coverage"][dir_name] = {
                "indexed_count": indexed_count,
                "path": dir_path
            }
        
        # Calculate coverage score
        results["critical_coverage_score"] = round(
            results["critical_files_indexed"] / len(CRITICAL_FILES), 3
        ) if CRITICAL_FILES else 1.0
        
        return results
    
    # =========================================================================
    # TEST 5: HYBRID VS PURE SEMANTIC
    # =========================================================================
    
    def test_hybrid_vs_semantic(self) -> Dict[str, Any]:
        """Compare hybrid search vs pure semantic search"""
        LOG.info("Testing hybrid vs pure semantic search...")
        
        results = {
            "tests_run": 0,
            "hybrid_wins": 0,
            "semantic_wins": 0,
            "ties": 0,
            "comparisons": []
        }
        
        test_queries = [
            "N5 meeting transcript ingestion pipeline",
            "CRM contact enrichment from Gmail",
            "warm intro networking email generator",
            "Careerspan SHRM application",
            "semantic embedding vector search",
        ]
        
        for query in test_queries:
            LOG.info(f"  Comparing for: {query[:40]}...")
            
            # Pure semantic search (bm25_weight=0)
            semantic_results = self.client.search(
                query=query,
                limit=10,
                use_hybrid=False
            )
            
            # Hybrid search (default weights)
            hybrid_results = self.client.search(
                query=query,
                limit=10,
                use_hybrid=True,
                semantic_weight=0.7,
                bm25_weight=0.3
            )
            
            # Compare results by checking keyword relevance
            query_terms = set(query.lower().split())
            
            def score_results(results):
                score = 0
                for i, r in enumerate(results[:5]):
                    content = r.get("content", "").lower()
                    path = r.get("path", "").lower()
                    term_matches = sum(1 for t in query_terms if t in content or t in path)
                    score += term_matches * (5 - i)  # Weight by position
                return score
            
            semantic_score = score_results(semantic_results)
            hybrid_score = score_results(hybrid_results)
            
            results["tests_run"] += 1
            
            winner = "tie"
            if hybrid_score > semantic_score * 1.1:  # 10% better threshold
                results["hybrid_wins"] += 1
                winner = "hybrid"
            elif semantic_score > hybrid_score * 1.1:
                results["semantic_wins"] += 1
                winner = "semantic"
            else:
                results["ties"] += 1
            
            results["comparisons"].append({
                "query": query,
                "semantic_score": semantic_score,
                "hybrid_score": hybrid_score,
                "winner": winner,
                "semantic_top3": [r.get("path", "")[:50] for r in semantic_results[:3]],
                "hybrid_top3": [r.get("path", "")[:50] for r in hybrid_results[:3]]
            })
        
        # Calculate recommendation
        if results["tests_run"] > 0:
            results["hybrid_win_rate"] = round(results["hybrid_wins"] / results["tests_run"], 3)
            results["semantic_win_rate"] = round(results["semantic_wins"] / results["tests_run"], 3)
            
            if results["hybrid_wins"] > results["semantic_wins"]:
                results["recommendation"] = "Use hybrid search (BM25 + semantic)"
            elif results["semantic_wins"] > results["hybrid_wins"]:
                results["recommendation"] = "Use pure semantic search"
            else:
                results["recommendation"] = "Both perform similarly - hybrid provides more diversity"
        
        return results
    
    # =========================================================================
    # GENERATE FULL REPORT
    # =========================================================================
    
    def run_all_tests(self) -> QualityReport:
        """Run all tests and generate comprehensive report"""
        LOG.info("=" * 60)
        LOG.info("N5 SEMANTIC MEMORY QUALITY ASSESSMENT")
        LOG.info("=" * 60)
        
        db_stats = self.get_db_stats()
        LOG.info(f"Database stats: {db_stats}")
        
        retrieval = self.test_retrieval_quality()
        coherence = self.test_embedding_coherence()
        chunking = self.test_chunking_quality()
        coverage = self.test_coverage_validation()
        hybrid_comparison = self.test_hybrid_vs_semantic()
        
        # Calculate overall score (weighted)
        scores = [
            retrieval.get("overall_score", 0) * 0.35,      # Retrieval is most important
            coherence.get("overall_score", 0) * 0.20,      # Embedding quality
            chunking.get("quality_score", 0) * 0.20,       # Chunk quality
            coverage.get("critical_coverage_score", 0) * 0.15,  # Coverage
            hybrid_comparison.get("hybrid_win_rate", 0.5) * 0.10  # Hybrid advantage
        ]
        overall_score = sum(scores)
        
        # Generate recommendations
        recommendations = []
        
        if retrieval.get("average_precision", 0) < 0.4:
            recommendations.append("Retrieval precision is low - consider reindexing with better chunking")
        
        if coherence.get("average_similarity", 0) < 0.4:
            recommendations.append("Embedding coherence is low - similar docs may not cluster well")
        
        if chunking.get("quality_score", 0) < 0.8:
            recommendations.append(f"Chunking has {chunking.get('issues_percentage', 0)}% issues - review chunking algorithm")
        
        if coverage.get("missing_critical"):
            recommendations.append(f"Missing {len(coverage['missing_critical'])} critical files - run reindex")
        
        if hybrid_comparison.get("hybrid_win_rate", 0) > 0.6:
            recommendations.append("Hybrid search performs better - ensure BM25 is enabled")
        elif hybrid_comparison.get("semantic_win_rate", 0) > 0.6:
            recommendations.append("Pure semantic search performs better - BM25 may add noise")
        
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring")
        
        return QualityReport(
            generated_at=datetime.datetime.now().isoformat(),
            db_stats=db_stats,
            retrieval_quality=retrieval,
            embedding_coherence=coherence,
            chunking_quality=chunking,
            coverage_validation=coverage,
            hybrid_vs_semantic=hybrid_comparison,
            overall_score=round(overall_score, 3),
            recommendations=recommendations
        )
    
    def generate_markdown_report(self, report: QualityReport) -> str:
        """Generate markdown report from QualityReport"""
        md = []
        md.append("---")
        md.append("created: " + datetime.date.today().isoformat())
        md.append("last_edited: " + datetime.date.today().isoformat())
        md.append("version: 1.0")
        md.append("---")
        md.append("")
        md.append("# N5 Semantic Memory Quality Assessment Report")
        md.append("")
        md.append(f"**Generated:** {report.generated_at}")
        md.append(f"**Overall Score:** {report.overall_score:.1%}")
        md.append("")
        
        # Summary box
        md.append("## 📊 Executive Summary")
        md.append("")
        status = "✅ HEALTHY" if report.overall_score >= 0.7 else "⚠️ NEEDS ATTENTION" if report.overall_score >= 0.5 else "❌ CRITICAL"
        md.append(f"| Metric | Score | Status |")
        md.append("|--------|-------|--------|")
        md.append(f"| **Overall** | {report.overall_score:.1%} | {status} |")
        md.append(f"| Retrieval Quality | {report.retrieval_quality.get('overall_score', 0):.1%} | {'✅' if report.retrieval_quality.get('overall_score', 0) >= 0.6 else '⚠️'} |")
        md.append(f"| Embedding Coherence | {report.embedding_coherence.get('overall_score', 0):.1%} | {'✅' if report.embedding_coherence.get('overall_score', 0) >= 0.6 else '⚠️'} |")
        md.append(f"| Chunking Quality | {report.chunking_quality.get('quality_score', 0):.1%} | {'✅' if report.chunking_quality.get('quality_score', 0) >= 0.8 else '⚠️'} |")
        md.append(f"| Coverage | {report.coverage_validation.get('critical_coverage_score', 0):.1%} | {'✅' if report.coverage_validation.get('critical_coverage_score', 0) >= 0.8 else '⚠️'} |")
        md.append("")
        
        # Database Stats
        md.append("## 📈 Database Statistics")
        md.append("")
        md.append(f"- **Total Resources:** {report.db_stats.get('total_resources', 0):,}")
        md.append(f"- **Total Blocks/Chunks:** {report.db_stats.get('total_blocks', 0):,}")
        md.append(f"- **Total Vectors:** {report.db_stats.get('total_vectors', 0):,}")
        md.append(f"- **Average Chunk Size:** {report.db_stats.get('avg_chunk_size', 0):,} chars")
        md.append(f"- **Chunk Size Range:** {report.db_stats.get('min_chunk_size', 0)} - {report.db_stats.get('max_chunk_size', 0)} chars")
        md.append("")
        
        # Retrieval Quality
        md.append("## 🔍 Retrieval Quality")
        md.append("")
        rq = report.retrieval_quality
        md.append(f"**Tests Passed:** {rq.get('tests_passed', 0)}/{rq.get('tests_run', 0)}")
        md.append(f"**Average Precision:** {rq.get('average_precision', 0):.1%}")
        md.append(f"**Average Recall:** {rq.get('average_recall', 0):.1%}")
        md.append("")
        
        md.append("### Individual Test Results")
        md.append("")
        for test in rq.get('individual_results', []):
            status = "✅" if test.get('passed') else "❌"
            md.append(f"#### {status} {test.get('name', 'Unknown')}")
            md.append(f"- Query: `{test.get('query', '')[:60]}`")
            md.append(f"- Precision: {test.get('precision', 0):.1%}")
            md.append(f"- Path Matches: {test.get('path_matches', 0)}")
            md.append(f"- Top Results:")
            for r in test.get('top_results', [])[:3]:
                md.append(f"  - `{r.get('path', '')}` (score: {r.get('score', 0):.4f})")
            md.append("")
        
        # Embedding Coherence
        md.append("## 🧬 Embedding Coherence")
        md.append("")
        ec = report.embedding_coherence
        md.append(f"**Tests Passed:** {ec.get('tests_passed', 0)}/{ec.get('tests_run', 0)}")
        md.append(f"**Average Similarity:** {ec.get('average_similarity', 0):.3f}")
        if 'self_similarity_avg' in ec:
            md.append(f"**Self-Similarity (same doc chunks):** avg={ec.get('self_similarity_avg', 0):.3f}, min={ec.get('self_similarity_min', 0):.3f}, max={ec.get('self_similarity_max', 0):.3f}")
        md.append("")
        
        for test in ec.get('individual_results', []):
            status = "✅" if test.get('passed') else "❌"
            md.append(f"- {status} **{test.get('name')}**: similarity={test.get('similarity', 0):.3f} (expected ≥{test.get('expected_min', 0):.2f})")
        md.append("")
        
        # Chunking Quality
        md.append("## ✂️ Chunking Quality")
        md.append("")
        cq = report.chunking_quality
        md.append(f"**Chunks Analyzed:** {cq.get('total_chunks_analyzed', 0)}")
        md.append(f"**Quality Score:** {cq.get('quality_score', 0):.1%}")
        md.append(f"**Issues Found:** {cq.get('issues_percentage', 0):.1f}%")
        md.append("")
        md.append("| Issue Type | Count |")
        md.append("|------------|-------|")
        md.append(f"| Truncated Sentences | {cq.get('truncated_sentences', 0)} |")
        md.append(f"| Broken Markdown | {cq.get('broken_markdown', 0)} |")
        md.append(f"| Orphan Headers | {cq.get('orphan_headers', 0)} |")
        md.append(f"| Too Small (<100 chars) | {cq.get('too_small_chunks', 0)} |")
        md.append(f"| Too Large (>3000 chars) | {cq.get('too_large_chunks', 0)} |")
        md.append(f"| Ideal Size (200-2000) | {cq.get('ideal_size_chunks', 0)} |")
        md.append("")
        
        if cq.get('examples_bad'):
            md.append("### Examples of Problematic Chunks")
            md.append("")
            for ex in cq.get('examples_bad', [])[:3]:
                md.append(f"**{ex.get('path')}** - Issues: {', '.join(ex.get('issues', []))}")
                md.append(f"```")
                md.append(f"...{ex.get('ending', '')}")
                md.append(f"```")
                md.append("")
        
        # Coverage Validation
        md.append("## 📁 Coverage Validation")
        md.append("")
        cv = report.coverage_validation
        md.append(f"**Critical Files Indexed:** {cv.get('critical_files_indexed', 0)}/{cv.get('critical_files_checked', 0)}")
        md.append("")
        
        if cv.get('missing_critical'):
            md.append("### ❌ Missing Critical Files")
            for f in cv.get('missing_critical', []):
                md.append(f"- `{f}`")
            md.append("")
        
        md.append("### Directory Coverage")
        md.append("")
        md.append("| Directory | Indexed Files |")
        md.append("|-----------|---------------|")
        for dir_name, info in cv.get('directory_coverage', {}).items():
            md.append(f"| {dir_name} | {info.get('indexed_count', 0)} |")
        md.append("")
        
        # Hybrid vs Semantic
        md.append("## ⚖️ Hybrid vs Pure Semantic Search")
        md.append("")
        hs = report.hybrid_vs_semantic
        md.append(f"**Tests Run:** {hs.get('tests_run', 0)}")
        md.append(f"**Hybrid Wins:** {hs.get('hybrid_wins', 0)} ({hs.get('hybrid_win_rate', 0):.1%})")
        md.append(f"**Semantic Wins:** {hs.get('semantic_wins', 0)} ({hs.get('semantic_win_rate', 0):.1%})")
        md.append(f"**Ties:** {hs.get('ties', 0)}")
        md.append(f"**Recommendation:** {hs.get('recommendation', 'N/A')}")
        md.append("")
        
        # Recommendations
        md.append("## 💡 Recommendations")
        md.append("")
        for i, rec in enumerate(report.recommendations, 1):
            md.append(f"{i}. {rec}")
        md.append("")
        
        md.append("---")
        md.append(f"*Report generated by semantic_memory_quality_test.py*")
        
        return "\n".join(md)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Semantic Memory Quality Assessment")
    parser.add_argument("--db", default="/home/workspace/N5/cognition/brain.db", help="Path to brain.db")
    parser.add_argument("--output", default=None, help="Output path (default: N5/logs/semantic_memory_test_YYYYMMDD.md)")
    args = parser.parse_args()
    
    # Default output path
    if args.output is None:
        today = datetime.date.today().strftime("%Y%m%d")
        args.output = f"/home/workspace/N5/logs/semantic_memory_test_{today}.md"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Run tests
    tester = SemanticMemoryQualityTester(db_path=args.db)
    report = tester.run_all_tests()
    
    # Generate and save report
    markdown = tester.generate_markdown_report(report)
    
    with open(args.output, 'w') as f:
        f.write(markdown)
    
    LOG.info("=" * 60)
    LOG.info(f"OVERALL SCORE: {report.overall_score:.1%}")
    LOG.info(f"Report saved to: {args.output}")
    LOG.info("=" * 60)
    
    print(f"\n✅ Quality assessment complete!")
    print(f"📊 Overall Score: {report.overall_score:.1%}")
    print(f"📄 Report: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

