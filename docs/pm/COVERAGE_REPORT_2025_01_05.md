# Code Coverage Report

**Date:** 2026-01-15  
**Report Type:** Automated Coverage Report  
**Status:** ✅ Tests Executed Successfully

---

## Test Execution Results

**Test Execution:** Tests executed using venv at `C:\Users\cfell\venvs\league_analyzer`.

**Test Results:**
- ✅ **424 tests passed**
- ❌ 0 tests failed
- ⚠️ 0 errors

**Total Tests:** 424

**Overall Coverage:** **76.0%** (5178 statements, 1245 missed)

---

## Executive Summary

This report provides an automated, reproducible view of code coverage after running the full test suite.

### Coverage Breakdown

**Overall Statistics:**
- **Statements:** 5178
- **Covered:** 3933
- **Missing:** 1245
- **Coverage:** 76.0%


---

## Coverage Targets (from Manifesto)

### Expected Coverage (per Manifesto):
- **Domain**: 100%
- **Application**: 90%+
- **Infrastructure**: 80%+

---

## Layer Coverage


### Domain Layer
- **Coverage:** 81.9%
- **Statements:** 2065
- **Covered:** 1692
- **Missing:** 373
- **Status:** ❌

### Application Layer
- **Coverage:** 48.4%
- **Statements:** 730
- **Covered:** 353
- **Missing:** 377
- **Status:** ❌

### Infrastructure Layer
- **Coverage:** 79.2%
- **Statements:** 2383
- **Covered:** 1888
- **Missing:** 495
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
- **Last Updated**: 2026-01-15T08:55:17.472351

---
