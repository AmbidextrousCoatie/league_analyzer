# Code Coverage Report

**Date:** 2026-01-07  
**Report Type:** Automated Coverage Report  
**Status:** ✅ Tests Executed Successfully

---

## Test Execution Results

**Test Execution:** Tests executed using venv at `C:\Users\cfell\venvs\league_analyzer`.

**Test Results:**
- ✅ **384 tests passed**
- ❌ 0 tests failed
- ⚠️ 0 errors

**Total Tests:** 384

**Overall Coverage:** **78.9%** (4494 statements, 947 missed)

---

## Executive Summary

This report provides an automated, reproducible view of code coverage after running the full test suite.

### Coverage Breakdown

**Overall Statistics:**
- **Statements:** 4494
- **Covered:** 3547
- **Missing:** 947
- **Coverage:** 78.9%


---

## Coverage Targets (from Manifesto)

### Expected Coverage (per Manifesto):
- **Domain**: 100%
- **Application**: 90%+
- **Infrastructure**: 80%+

---

## Layer Coverage


### Domain Layer
- **Coverage:** 81.8%
- **Statements:** 2072
- **Covered:** 1694
- **Missing:** 378
- **Status:** ❌

### Application Layer
- **Coverage:** 0.0%
- **Statements:** 34
- **Covered:** 0
- **Missing:** 34
- **Status:** ❌

### Infrastructure Layer
- **Coverage:** 77.6%
- **Statements:** 2388
- **Covered:** 1853
- **Missing:** 535
- **Status:** ⚠️

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
- ✅ **All tests passing**

### Coverage Status
- ⚠️ **Overall coverage below target but improving**

---

## Notes

- **Reproducible**: This report is generated automatically and can be regenerated at any time
- **Integration**: This script is integrated with the regression testing system
- **Coverage Goals**: Aim for 100% domain, 90%+ application, 80%+ infrastructure per manifesto
- **Last Updated**: 2026-01-07T11:48:34.474685

---
