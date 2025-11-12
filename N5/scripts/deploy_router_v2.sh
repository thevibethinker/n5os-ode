#!/bin/bash
# Deploy Persona Router v2 for improved demo reliability
# Usage: bash /home/workspace/N5/scripts/deploy_router_v2.sh [--backup-only | --deploy | --revert]

set -e

SCRIPT_DIR="/home/workspace/N5/scripts"
V1_FILE="$SCRIPT_DIR/persona_router.py"
V2_FILE="$SCRIPT_DIR/persona_router_v2.py"
BACKUP_FILE="$SCRIPT_DIR/persona_router_v1_backup_$(date +%Y%m%d_%H%M%S).py"

show_usage() {
    cat << EOF
Persona Router v2 Deployment Script

Usage:
    bash deploy_router_v2.sh [option]

Options:
    --backup-only    Create backup of v1 without deploying v2
    --deploy         Backup v1 and deploy v2 (replace v1)
    --revert         Restore most recent v1 backup
    --test           Run comparison tests only
    --help           Show this help message

No option: Interactive mode (asks for confirmation)

EOF
}

backup_v1() {
    if [ -f "$V1_FILE" ]; then
        echo "📦 Backing up v1 to: $BACKUP_FILE"
        cp "$V1_FILE" "$BACKUP_FILE"
        echo "✓ Backup complete"
    else
        echo "⚠️  Warning: No v1 file found at $V1_FILE"
        exit 1
    fi
}

deploy_v2() {
    if [ ! -f "$V2_FILE" ]; then
        echo "❌ Error: v2 file not found at $V2_FILE"
        exit 1
    fi
    
    echo "🚀 Deploying v2..."
    cp "$V2_FILE" "$V1_FILE"
    echo "✓ v2 deployed as persona_router.py"
    echo ""
    echo "Verify deployment:"
    python3 "$V1_FILE" test | head -20
}

revert_to_v1() {
    # Find most recent backup
    LATEST_BACKUP=$(ls -t "$SCRIPT_DIR"/persona_router_v1_backup_*.py 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ Error: No v1 backups found"
        exit 1
    fi
    
    echo "🔄 Reverting to: $LATEST_BACKUP"
    cp "$LATEST_BACKUP" "$V1_FILE"
    echo "✓ Reverted to v1"
}

run_tests() {
    echo "🧪 Running comparison tests..."
    echo ""
    python3 "$V2_FILE" compare
    echo ""
    echo "📊 Running v2 full test suite..."
    python3 "$V2_FILE" test | grep -E "(Test [0-9]+:|Confidence:|Should Switch:)"
}

# Main logic
case "${1:-}" in
    --backup-only)
        backup_v1
        ;;
    --deploy)
        backup_v1
        deploy_v2
        ;;
    --revert)
        revert_to_v1
        ;;
    --test)
        run_tests
        ;;
    --help)
        show_usage
        exit 0
        ;;
    "")
        # Interactive mode
        echo "=================================="
        echo "Persona Router v2 Deployment"
        echo "=================================="
        echo ""
        echo "This will:"
        echo "  1. Backup current persona_router.py"
        echo "  2. Replace it with persona_router_v2.py"
        echo ""
        echo "v2 Improvements:"
        echo "  ✓ Fixes 70% confidence failures (Explain, Write queries)"
        echo "  ✓ All 12 test cases now achieve 100% confidence"
        echo "  ✓ Exact phrase matching for common patterns"
        echo "  ✓ Enhanced scoring with combo bonuses"
        echo ""
        read -p "Proceed with deployment? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            backup_v1
            deploy_v2
            echo ""
            echo "✅ Deployment complete!"
            echo ""
            echo "To revert: bash $0 --revert"
        else
            echo "Deployment cancelled"
            exit 0
        fi
        ;;
    *)
        echo "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
