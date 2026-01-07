# Regression Testing System

This project includes a regression testing system that prevents pushing code to remote if any previously passing test fails.

## Overview

The regression testing system:
1. **Tracks** which tests pass
2. **Compares** current test results with the baseline
3. **Blocks** git push if any previously passing test now fails
4. **Allows** updating the baseline when tests are fixed

## Quick Start

### 1. Install the Pre-Push Hook

```bash
python scripts/install_pre_push_hook.py
```

This installs a git pre-push hook that automatically runs regression checks before pushing.

### 2. Create Initial Baseline

After fixing tests and ensuring they pass, create a baseline:

```bash
python scripts/regression_test.py update
```

This runs all tests and saves the list of passing tests as the baseline.

### 3. Normal Workflow

- **Make changes** to code
- **Run tests** to verify changes: `pytest`
- **Try to push**: `git push`
  - If any previously passing test fails, the push is blocked
  - Fix the failing tests and try again
- **After fixing tests**, update baseline: `python scripts/regression_test.py update`

## Commands

### Check for Regressions

```bash
python scripts/regression_test.py check
```

Compares current test results (if available) with baseline. Returns exit code 1 if regressions found.

### Update Baseline

```bash
python scripts/regression_test.py update
```

Runs all tests and updates the baseline with currently passing tests. Use this after fixing tests.

### Run Tests and Check

```bash
python scripts/regression_test.py run
```

Runs all tests, saves results, and checks for regressions. This is what the pre-push hook does.

## How It Works

1. **Baseline File** (`.test_baseline.json`):
   - Stores a list of test names that passed when baseline was created
   - Not committed to git (in `.gitignore`)
   - Created/updated manually with `update` command

2. **Test Results File** (`.test_results.json`):
   - Stores current test run results
   - Not committed to git
   - Created automatically when tests run

3. **Pre-Push Hook** (`.git/hooks/pre-push`):
   - Automatically runs before `git push`
   - Executes `regression_test.py run`
   - Blocks push if regressions detected
   - Can be bypassed with `git push --no-verify` (not recommended)

## Example Workflow

```bash
# 1. Fix some failing tests
pytest  # See which tests fail

# 2. Fix the code/tests
# ... make changes ...

# 3. Verify tests pass
pytest  # All tests should pass now

# 4. Update baseline (tests are now passing)
python scripts/regression_test.py update

# 5. Make more changes
# ... make changes ...

# 6. Run tests
pytest  # Some tests might fail

# 7. Try to push
git push
# ❌ Push blocked! Regression detected in test_xyz

# 8. Fix the regression
# ... fix the test ...

# 9. Verify and update baseline
pytest
python scripts/regression_test.py update

# 10. Push again
git push
# ✅ Push succeeds!
```

## Bypassing the Hook

If you need to bypass the regression check (not recommended):

```bash
git push --no-verify
```

**Warning**: Only bypass if you're certain about what you're doing. The regression check helps prevent breaking previously working functionality.

## Troubleshooting

### "No baseline found"

If you see this message, create a baseline:

```bash
python scripts/regression_test.py update
```

### Hook not running

Verify the hook is installed:

```bash
ls -la .git/hooks/pre-push
```

Reinstall if needed:

```bash
python scripts/install_pre_push_hook.py
```

### Tests taking too long

The regression check runs all tests. For faster feedback during development:

- Run specific test files: `pytest tests/domain/test_entities_game.py`
- Use pytest markers: `pytest -m unit`
- Run tests in parallel: `pytest -n auto`

The pre-push hook will still run full regression check before pushing.

## Integration with CI/CD

The regression testing system is designed for local development. For CI/CD:

1. Run full test suite in CI
2. Fail build if any test fails
3. Don't rely on baseline comparison in CI (always run all tests)

## Files

- `scripts/regression_test.py` - Main regression testing script
- `scripts/pre-push-hook.sh` - Bash hook for Unix/Mac
- `scripts/pre-push-hook.ps1` - PowerShell hook for Windows
- `scripts/install_pre_push_hook.py` - Hook installer
- `.test_baseline.json` - Baseline file (gitignored)
- `.test_results.json` - Current test results (gitignored)

