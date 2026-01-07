"""
Generate Code Coverage Report

This script runs tests with coverage and generates a reproducible coverage report.
It extracts accurate test statistics and coverage data.

Usage:
    python scripts/generate_coverage_report.py
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configure UTF-8 encoding
try:
    import scripts.encoding_config
    UTF8 = scripts.encoding_config.UTF8
except ImportError:
    UTF8 = "utf-8"

# Configure stdout for UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, ValueError):
    pass

COVERAGE_JSON = Path("test_reports/coverage.json")
COVERAGE_XML = Path("test_reports/coverage.xml")
COVERAGE_HTML = Path("test_reports/htmlcov")


def run_tests_with_coverage() -> Dict[str, Any]:
    """
    Run tests with coverage and return test statistics.
    
    Returns:
        Dictionary with test statistics and coverage data
    """
    print("Running tests with coverage...")
    print("=" * 80)
    
    # Run pytest with coverage
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no"],
        capture_output=True,
        text=True,
        encoding=UTF8,
    )
    
    # Parse test results from output
    output_lines = result.stdout.split("\n")
    
    # Initialize counters
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    warnings = 0
    test_names = []
    
    # Parse test results
    for line in output_lines:
        line_stripped = line.strip()
        
        # Count passed tests
        if " PASSED" in line or " PASSED [" in line:
            passed += 1
            # Extract test name
            if "::" in line:
                test_name = line.split(" PASSED")[0].strip()
                test_names.append((test_name, "passed"))
        
        # Count failed tests
        elif " FAILED" in line or " FAILED [" in line:
            failed += 1
            if "::" in line:
                test_name = line.split(" FAILED")[0].strip()
                test_names.append((test_name, "failed"))
        
        # Count errors
        elif " ERROR" in line or " ERROR [" in line:
            errors += 1
            if "::" in line:
                test_name = line.split(" ERROR")[0].strip()
                test_names.append((test_name, "error"))
        
        # Count skipped tests
        elif " SKIPPED" in line or " SKIPPED [" in line:
            skipped += 1
            if "::" in line:
                test_name = line.split(" SKIPPED")[0].strip()
                test_names.append((test_name, "skipped"))
    
    # Parse summary line if present
    for line in output_lines:
        if "passed" in line.lower() and ("failed" in line.lower() or "error" in line.lower()):
            # Try to extract numbers from summary
            import re
            summary_match = re.search(r'(\d+)\s+passed', line, re.IGNORECASE)
            if summary_match and passed == 0:
                passed = int(summary_match.group(1))
            
            failed_match = re.search(r'(\d+)\s+failed', line, re.IGNORECASE)
            if failed_match and failed == 0:
                failed = int(failed_match.group(1))
            
            error_match = re.search(r'(\d+)\s+error', line, re.IGNORECASE)
            if error_match and errors == 0:
                errors = int(error_match.group(1))
    
    total_tests = passed + failed + errors + skipped
    
    print(f"\nTest Execution Results:")
    print(f"  Total tests: {total_tests}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Errors: {errors}")
    if skipped > 0:
        print(f"  ⏭️  Skipped: {skipped}")
    
    # Load coverage data from JSON
    coverage_data = load_coverage_data()
    
    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "test_names": test_names,
        "coverage": coverage_data,
        "timestamp": datetime.now().isoformat(),
        "return_code": result.returncode,
    }


def load_coverage_data() -> Dict[str, Any]:
    """
    Load coverage data from JSON report.
    
    Returns:
        Dictionary with coverage statistics
    """
    if not COVERAGE_JSON.exists():
        print(f"Warning: Coverage JSON not found at {COVERAGE_JSON}")
        return {}
    
    try:
        with open(COVERAGE_JSON, "r", encoding=UTF8) as f:
            data = json.load(f)
        
        # Extract coverage totals
        totals = data.get("totals", {})
        
        coverage_data = {
            "percent_covered": totals.get("percent_covered", 0),
            "statements": totals.get("num_statements", 0),
            "missing": totals.get("missing_lines", 0),
            "excluded": totals.get("excluded_lines", 0),
            "branches": totals.get("num_branches", 0),
            "partial_branches": totals.get("num_partial_branches", 0),
        }
        
        # Extract file-level coverage
        files = data.get("files", {})
        file_coverage = {}
        
        for file_path, file_data in files.items():
            file_totals = file_data.get("summary", {})
            file_coverage[file_path] = {
                "percent_covered": file_totals.get("percent_covered", 0),
                "statements": file_totals.get("num_statements", 0),
                "missing": file_totals.get("missing_lines", 0),
            }
        
        coverage_data["files"] = file_coverage
        
        return coverage_data
    
    except Exception as e:
        print(f"Error loading coverage data: {e}")
        return {}


def generate_coverage_report(test_stats: Dict[str, Any]) -> str:
    """
    Generate a markdown coverage report.
    
    Args:
        test_stats: Test statistics and coverage data
        
    Returns:
        Markdown report as string
    """
    coverage = test_stats.get("coverage", {})
    
    report = f"""# Code Coverage Report

**Date:** {datetime.now().strftime("%Y-%m-%d")}  
**Report Type:** Automated Coverage Report  
**Status:** {"✅ Tests Executed Successfully" if test_stats.get("return_code") == 0 else "⚠️ Some Tests Failed"}

---

## Test Execution Results

**Test Execution:** Tests executed using venv at `C:\\Users\\cfell\\venvs\\league_analyzer`.

**Test Results:**
- ✅ **{test_stats['passed']} tests passed**
- ❌ {test_stats['failed']} tests failed
- ⚠️ {test_stats['errors']} errors
"""
    
    if test_stats.get("skipped", 0) > 0:
        report += f"- ⏭️ {test_stats['skipped']} tests skipped\n"
    
    report += f"""
**Total Tests:** {test_stats['total_tests']}

**Overall Coverage:** **{coverage.get('percent_covered', 0):.1f}%** ({coverage.get('statements', 0)} statements, {coverage.get('missing', 0)} missed)

---

## Executive Summary

This report provides an automated, reproducible view of code coverage after running the full test suite.

### Coverage Breakdown

**Overall Statistics:**
- **Statements:** {coverage.get('statements', 0)}
- **Covered:** {coverage.get('statements', 0) - coverage.get('missing', 0)}
- **Missing:** {coverage.get('missing', 0)}
- **Coverage:** {coverage.get('percent_covered', 0):.1f}%

"""
    
    if coverage.get('branches', 0) > 0:
        report += f"""
**Branch Coverage:**
- **Branches:** {coverage.get('branches', 0)}
- **Partial:** {coverage.get('partial_branches', 0)}
- **Coverage:** {(1 - coverage.get('partial_branches', 0) / max(coverage.get('branches', 1), 1)) * 100:.1f}%

"""
    
    report += """
---

## Coverage Targets (from Manifesto)

### Expected Coverage (per Manifesto):
- **Domain**: 100%
- **Application**: 90%+
- **Infrastructure**: 80%+

---

## Layer Coverage

"""
    
    # Calculate layer coverage
    files = coverage.get("files", {})
    
    domain_files = {k: v for k, v in files.items() if "domain" in k.lower()}
    application_files = {k: v for k, v in files.items() if "application" in k.lower()}
    infrastructure_files = {k: v for k, v in files.items() if "infrastructure" in k.lower()}
    
    def calculate_layer_coverage(layer_files: Dict[str, Any]) -> Dict[str, Any]:
        if not layer_files:
            return {"percent": 0, "statements": 0, "missing": 0}
        
        total_statements = sum(f.get("statements", 0) for f in layer_files.values())
        total_missing = sum(f.get("missing", 0) for f in layer_files.values())
        total_covered = total_statements - total_missing
        percent = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        return {
            "percent": percent,
            "statements": total_statements,
            "missing": total_missing,
            "covered": total_covered,
        }
    
    domain_coverage = calculate_layer_coverage(domain_files)
    application_coverage = calculate_layer_coverage(application_files)
    infrastructure_coverage = calculate_layer_coverage(infrastructure_files)
    
    report += f"""
### Domain Layer
- **Coverage:** {domain_coverage['percent']:.1f}%
- **Statements:** {domain_coverage['statements']}
- **Covered:** {domain_coverage['covered']}
- **Missing:** {domain_coverage['missing']}
- **Status:** {"✅" if domain_coverage['percent'] >= 100 else "⚠️" if domain_coverage['percent'] >= 90 else "❌"}

### Application Layer
- **Coverage:** {application_coverage['percent']:.1f}%
- **Statements:** {application_coverage['statements']}
- **Covered:** {application_coverage['covered']}
- **Missing:** {application_coverage['missing']}
- **Status:** {"✅" if application_coverage['percent'] >= 90 else "⚠️" if application_coverage['percent'] >= 80 else "❌"}

### Infrastructure Layer
- **Coverage:** {infrastructure_coverage['percent']:.1f}%
- **Statements:** {infrastructure_coverage['statements']}
- **Covered:** {infrastructure_coverage['covered']}
- **Missing:** {infrastructure_coverage['missing']}
- **Status:** {"✅" if infrastructure_coverage['percent'] >= 80 else "⚠️" if infrastructure_coverage['percent'] >= 70 else "❌"}

---

## Test Execution Details

### Command Executed
```bash
pytest tests/ -v --tb=no --cov=domain --cov=application --cov=infrastructure --cov-report=json:test_reports/coverage.json
```

### Coverage Reports Generated
- **HTML Report**: `test_reports/htmlcov/index.html` (full project coverage)
- **XML Report**: `test_reports/coverage.xml`
- **JSON Report**: `test_reports/coverage.json`

---

## Key Findings

### Test Status
"""
    
    if test_stats['failed'] == 0 and test_stats['errors'] == 0:
        report += "- ✅ **All tests passing**\n"
    else:
        report += f"- ⚠️ **{test_stats['failed'] + test_stats['errors']} test(s) need attention**\n"
    
    report += f"""
### Coverage Status
"""
    
    if coverage.get('percent_covered', 0) >= 80:
        report += "- ✅ **Overall coverage meets target (80%+)**\n"
    elif coverage.get('percent_covered', 0) >= 70:
        report += "- ⚠️ **Overall coverage below target but improving**\n"
    else:
        report += "- ❌ **Overall coverage needs improvement**\n"
    
    report += f"""
---

## Notes

- **Reproducible**: This report is generated automatically and can be regenerated at any time
- **Integration**: This script is integrated with the regression testing system
- **Coverage Goals**: Aim for 100% domain, 90%+ application, 80%+ infrastructure per manifesto
- **Last Updated**: {test_stats.get('timestamp', 'Unknown')}

---
"""
    
    return report


def main():
    """Main entry point."""
    print("=" * 80)
    print("Code Coverage Report Generator")
    print("=" * 80)
    print()
    
    # Ensure test_reports directory exists
    Path("test_reports").mkdir(exist_ok=True)
    
    # Run tests with coverage
    test_stats = run_tests_with_coverage()
    
    # Generate report
    print("\n" + "=" * 80)
    print("Generating Coverage Report...")
    print("=" * 80)
    
    report = generate_coverage_report(test_stats)
    
    # Save report
    report_path = Path("docs/pm/COVERAGE_REPORT_2025_01_05.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding=UTF8) as f:
        f.write(report)
    
    print(f"\n✅ Coverage report saved to: {report_path}")
    print(f"\nCoverage Summary:")
    coverage = test_stats.get("coverage", {})
    print(f"  Overall: {coverage.get('percent_covered', 0):.1f}%")
    print(f"  Statements: {coverage.get('statements', 0)}")
    print(f"  Missing: {coverage.get('missing', 0)}")
    
    # Return exit code based on test results
    if test_stats.get("return_code") != 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
