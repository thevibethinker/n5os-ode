#!/usr/bin/env python3
"""Rebuild the HNSW ANN index for brain.db semantic search.

Usage:
    python3 N5/scripts/n5_rebuild_ann_index.py
    python3 N5/scripts/n5_rebuild_ann_index.py --ef 200 --M 16

After bulk indexing operations (n5_index_embeddings.py, n5_index_rebuild.py),
run this script to rebuild the ANN index for fast search.
"""
import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
LOG = logging.getLogger(__name__)

sys.path.insert(0, "/home/workspace/N5/cognition")

def main():
    parser = argparse.ArgumentParser(description="Rebuild ANN index for brain.db")
    parser.add_argument("--ef", type=int, default=200, 
                        help="ef_construction parameter (higher = better recall, slower build)")
    parser.add_argument("--M", type=int, default=16, 
                        help="M parameter (connections per node, higher = better recall, more memory)")
    args = parser.parse_args()
    
    from n5_memory_client import N5MemoryClient, HAS_HNSWLIB, ANN_INDEX_PATH
    
    if not HAS_HNSWLIB:
        LOG.error("hnswlib not installed. Run: pip install hnswlib")
        sys.exit(1)
    
    LOG.info("Initializing N5MemoryClient...")
    client = N5MemoryClient()
    
    LOG.info(f"Building ANN index with ef_construction={args.ef}, M={args.M}")
    success = client.rebuild_ann_index(ef_construction=args.ef, M=args.M)
    
    if success:
        LOG.info(f"ANN index saved to: {ANN_INDEX_PATH}")
        LOG.info(f"ID mapping saved to: {ANN_INDEX_PATH}.ids")
        sys.exit(0)
    else:
        LOG.error("Failed to rebuild ANN index")
        sys.exit(1)

if __name__ == "__main__":
    main()

