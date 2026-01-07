#!/bin/bash
#
# Git pre-push hook for regression testing
# 
# This hook prevents pushing to remote if any previously passing test fails.
#
# Installation:
#   cp scripts/pre-push-hook.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push
#
# Or on Windows (Git Bash):
#   cp scripts/pre-push-hook.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT" || exit 1

# Check if baseline exists
if [ ! -f ".test_baseline.json" ]; then
    echo "⚠️  No test baseline found."
    echo "   Run 'python scripts/regression_test.py update' to create a baseline."
    echo ""
    echo "   Proceeding with push (no baseline to check against)..."
    exit 0
fi

# Run regression check
echo "Running regression tests..."
python scripts/regression_test.py run

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Regression tests failed. Push aborted."
    echo ""
    echo "To fix:"
    echo "  1. Fix the failing tests"
    echo "  2. Run 'python scripts/regression_test.py update' to update baseline"
    echo "  3. Try pushing again"
    echo ""
    echo "To bypass this check (not recommended):"
    echo "  git push --no-verify"
    exit 1
fi

echo "✅ Regression tests passed. Proceeding with push..."
exit 0

