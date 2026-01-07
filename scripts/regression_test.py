"""
Regression Testing System

Tracks which tests pass and prevents pushing to remote if any previously
passing test fails (regresses).

Usage:
    python scripts/regression_test.py check    # Check for regressions
    python scripts/regression_test.py update   # Update baseline after fixing tests
    python scripts/regression_test.py run      # Run tests and check for regressions
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime

# Configure UTF-8 encoding
try:
    import scripts.encoding_config
    UTF8 = scripts.encoding_config.UTF8
except ImportError:
    UTF8 = "utf-8"


BASELINE_FILE = Path(".test_baseline.json")
TEST_RESULTS_FILE = Path(".test_results.json")


def run_tests() -> Dict[str, bool]:
    """
    Run all tests and return a dictionary mapping test names to pass/fail status.
    
    Returns:
        Dictionary with test names as keys and True (passed) / False (failed) as values
    """
    print("Collecting test names...")
    
    # Collect all test names using pytest's collect-only with quiet mode
    # This gives cleaner output
    collect_result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/"],
        capture_output=True,
        text=True,
        encoding=UTF8,
    )
    
    # Parse test names from tree format output
    # Format: <Package tests>
    #         <Package domain>
    #         <Module test_entities_game.py>
    #         <Class TestGame>
    #         <Function test_create_valid_game>
    # Becomes: tests/domain/test_entities_game.py::TestGame::test_create_valid_game
    test_names = []
    package_stack = []  # Stack to track package hierarchy with indentation: [(indent, name), ...]
    current_module = None
    current_class = None
    
    for line in collect_result.stdout.split("\n"):
        original_line = line
        stripped_line = line.strip()
        
        # Skip empty lines and summary lines
        if not stripped_line:
            continue
        if (stripped_line.startswith("=") or stripped_line.startswith("platform") or 
            stripped_line.startswith("cachedir") or stripped_line.startswith("rootdir") or 
            stripped_line.startswith("configfile") or stripped_line.startswith("plugins") or 
            stripped_line.startswith("asyncio") or stripped_line.startswith("collecting") or
            stripped_line.startswith("collected")):
            continue
        
        # Calculate indentation level (number of leading spaces)
        indent_level = len(line) - len(line.lstrip())
        
        # Track package hierarchy: <Package tests>, <Package domain>
        if stripped_line.startswith("<Package "):
            package_name = stripped_line.replace("<Package ", "").replace(">", "").strip()
            if ">" in package_name:
                package_name = package_name.split(">")[0].strip()
            
            # Only track packages that are part of the tests directory
            if package_name == "tests" or (package_stack and package_stack[0][1] == "tests"):
                # Remove packages at deeper or equal indentation levels (we're going back up the tree)
                while package_stack and package_stack[-1][0] >= indent_level:
                    package_stack.pop()
                package_stack.append((indent_level, package_name))
            continue
        
        # Skip <Dir> tags
        if stripped_line.startswith("<Dir "):
            continue
        
        # Match module lines: <Module test_entities_game.py>
        if stripped_line.startswith("<Module "):
            # Extract module filename: <Module test_entities_game.py>
            module_filename = stripped_line.replace("<Module ", "").replace(">", "").strip()
            # Handle cases where there might be extra text after >
            if ">" in module_filename:
                module_filename = module_filename.split(">")[0].strip()
            
            # Build full module path from package stack
            if package_stack and package_stack[0][1] == "tests":
                # Extract just the package names (ignore indent levels)
                package_names = [pkg[1] for pkg in package_stack]
                # Join package path and module filename
                module_path = "/".join(package_names) + "/" + module_filename
                # Convert to use forward slashes (pytest uses forward slashes even on Windows)
                module_path = module_path.replace("\\", "/")
                current_module = module_path
                current_class = None  # Reset class when new module starts
            else:
                # If we don't have a proper package path, try to use the filename directly
                if module_filename.startswith("tests/"):
                    current_module = module_filename
                    current_class = None
        
        # Match class lines: <Class TestGame>
        elif stripped_line.startswith("<Class "):
            # Extract class name: <Class TestGame>
            class_match = stripped_line.replace("<Class ", "").replace(">", "").strip()
            # Handle cases where there might be extra text after >
            if ">" in class_match:
                class_match = class_match.split(">")[0].strip()
            # Only set class if we have a current module
            if current_module:
                current_class = class_match
        
        # Match function lines: <Function test_create_valid_game>
        elif stripped_line.startswith("<Function ") and current_module:
            # Extract function name: <Function test_create_valid_game>
            function_match = stripped_line.replace("<Function ", "").replace(">", "").strip()
            # Handle cases where there might be extra text after >
            if ">" in function_match:
                function_match = function_match.split(">")[0].strip()
            
            # Skip fixtures (they have < in the name), but include parameterized tests
            if "<" in function_match:
                continue
            
            # Build full test name
            if current_class:
                test_name = f"{current_module}::{current_class}::{function_match}"
            else:
                test_name = f"{current_module}::{function_match}"
            
            if test_name not in test_names:
                test_names.append(test_name)
    
    if not test_names:
        print("Warning: No tests found. Check that tests/ directory exists and contains test files.")
        print(f"Collect output (first 1500 chars):\n{collect_result.stdout[:1500]}")
        print(f"\nStderr (first 500 chars):\n{collect_result.stderr[:500]}")
        return {}
    
    print(f"Found {len(test_names)} tests")
    print("Running tests...")
    
    # Run all tests at once and parse results
    # This is faster than running individually
    run_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=no", "tests/"],
        capture_output=True,
        text=True,
        encoding=UTF8,
    )
    
    # Parse test results from output
    # Format: tests/domain/test_entities_game.py::TestGame::test_create_valid_game PASSED
    # or:     tests/domain/test_entities_game.py::TestGame::test_create_valid_game FAILED
    test_results = {}
    
    # Initialize all tests as failed
    for test_name in test_names:
        test_results[test_name] = False
    
    # Parse output to find passed tests
    output_lines = run_result.stdout.split("\n")
    for line in output_lines:
        line = line.strip()
        # Look for lines like: "tests/...::...::test_... PASSED"
        if " PASSED" in line or " PASSED [" in line:
            # Extract test name (everything before " PASSED")
            test_name = line.split(" PASSED")[0].strip()
            if test_name in test_results:
                test_results[test_name] = True
        elif " FAILED" in line or " FAILED [" in line:
            # Extract test name (everything before " FAILED")
            test_name = line.split(" FAILED")[0].strip()
            if test_name in test_results:
                test_results[test_name] = False
    
    # If parsing failed, run tests individually as fallback
    if not any(test_results.values()) and len(test_names) > 0:
        print("Parsing failed, running tests individually...")
        for i, test_name in enumerate(test_names, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(test_names)}")
            
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", test_name, "-v", "--tb=no"],
                capture_output=True,
                text=True,
                encoding=UTF8,
            )
            test_results[test_name] = test_result.returncode == 0
    
    return test_results


def load_baseline() -> Dict[str, bool]:
    """Load the baseline of previously passing tests."""
    if not BASELINE_FILE.exists():
        return {}
    
    try:
        with open(BASELINE_FILE, "r", encoding=UTF8) as f:
            data = json.load(f)
            return data.get("passing_tests", {})
    except Exception as e:
        print(f"Warning: Could not load baseline: {e}")
        return {}


def save_baseline(passing_tests: Dict[str, bool]):
    """Save the baseline of passing tests."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "passing_tests": passing_tests,
    }
    
    with open(BASELINE_FILE, "w", encoding=UTF8) as f:
        json.dump(data, f, indent=2)
    
    print(f"Baseline saved: {len(passing_tests)} passing tests")


def save_test_results(test_results: Dict[str, bool]):
    """Save current test results."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "test_results": test_results,
    }
    
    with open(TEST_RESULTS_FILE, "w", encoding=UTF8) as f:
        json.dump(data, f, indent=2)


def find_regressions(current_results: Dict[str, bool], baseline: Dict[str, bool]) -> List[str]:
    """
    Find tests that passed in baseline but fail now.
    
    Args:
        current_results: Current test results (test_name -> passed)
        baseline: Baseline test results (test_name -> passed)
    
    Returns:
        List of test names that regressed
    """
    regressions = []
    
    for test_name, was_passing in baseline.items():
        if was_passing:
            # This test was passing before
            if test_name not in current_results:
                # Test was removed or renamed
                regressions.append(f"{test_name} (test removed or renamed)")
            elif not current_results[test_name]:
                # Test now fails
                regressions.append(test_name)
    
    return regressions


def check_regressions() -> bool:
    """
    Check for regressions by comparing current test results with baseline.
    
    Returns:
        True if no regressions found, False otherwise
    """
    baseline = load_baseline()
    
    if not baseline:
        print("No baseline found. Run 'python scripts/regression_test.py update' first.")
        return True  # No baseline means no regressions to check
    
    # Load current results if available, otherwise run tests
    if TEST_RESULTS_FILE.exists():
        try:
            with open(TEST_RESULTS_FILE, "r", encoding=UTF8) as f:
                data = json.load(f)
                current_results = data.get("test_results", {})
        except Exception:
            current_results = {}
    else:
        current_results = {}
    
    if not current_results:
        print("No current test results found. Running tests...")
        current_results = run_tests()
        save_test_results(current_results)
    
    regressions = find_regressions(current_results, baseline)
    
    if regressions:
        print("\n" + "="*80)
        print("REGRESSION DETECTED!")
        print("="*80)
        print(f"\n{len(regressions)} test(s) that previously passed are now failing:\n")
        for test_name in regressions:
            print(f"  ❌ {test_name}")
        print("\n" + "="*80)
        print("Please fix these tests before pushing to remote.")
        print("="*80 + "\n")
        return False
    else:
        print("\n✅ No regressions detected. All previously passing tests still pass.")
        return True


def update_baseline():
    """Update the baseline with current passing tests."""
    print("Running tests to establish baseline...")
    test_results = run_tests()
    
    # Only include passing tests in baseline
    passing_tests = {name: True for name, passed in test_results.items() if passed}
    
    save_baseline(passing_tests)
    save_test_results(test_results)
    
    total = len(test_results)
    passing = sum(1 for v in test_results.values() if v)
    failing = total - passing
    
    print(f"\nBaseline updated:")
    print(f"  Total tests: {total}")
    print(f"  Passing: {passing}")
    print(f"  Failing: {failing}")
    
    if failing > 0:
        print(f"\n⚠️  Warning: {failing} test(s) are currently failing.")
        print("   These will not be included in the baseline.")


def main():
    """Main entry point."""
    # Configure stdout for UTF-8 encoding to handle emojis
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Python < 3.7 or already configured
        pass
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/regression_test.py check     # Check for regressions")
        print("  python scripts/regression_test.py update     # Update baseline")
        print("  python scripts/regression_test.py run        # Run tests and check")
        print("  python scripts/regression_test.py coverage   # Generate coverage report")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        success = check_regressions()
        sys.exit(0 if success else 1)
    elif command == "update":
        update_baseline()
        # Also generate coverage report
        print("\n" + "="*80)
        print("Generating coverage report...")
        print("="*80)
        try:
            # Import and run coverage report generator
            import importlib.util
            coverage_script = Path(__file__).parent / "generate_coverage_report.py"
            spec = importlib.util.spec_from_file_location("generate_coverage_report", coverage_script)
            coverage_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(coverage_module)
            coverage_module.main()
        except Exception as e:
            print(f"Warning: Could not generate coverage report: {e}")
        sys.exit(0)
    elif command == "run":
        test_results = run_tests()
        save_test_results(test_results)
        success = check_regressions()
        sys.exit(0 if success else 1)
    elif command == "coverage":
        # Generate coverage report
        try:
            # Import and run coverage report generator
            import importlib.util
            coverage_script = Path(__file__).parent / "generate_coverage_report.py"
            spec = importlib.util.spec_from_file_location("generate_coverage_report", coverage_script)
            coverage_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(coverage_module)
            coverage_module.main()
        except Exception as e:
            print(f"Error generating coverage report: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

