# Quick Start for Worker 3

## Import Module
from Intelligence.scripts import block_db

## Log Generation
gen_id = block_db.log_generation(block_id="B01", meeting_id="M123", status="pending")

## Update Success
block_db.update_generation(gen_id, status="success", output_path="/path")
block_db.update_block_stats("B01", success=True)

## Update Failure  
block_db.update_generation(gen_id, status="failed", error_message="...")
block_db.update_block_stats("B01", success=False)

## Get Block
block = block_db.get_block("B01")

## List Blocks
blocks = block_db.list_blocks(status="active")
