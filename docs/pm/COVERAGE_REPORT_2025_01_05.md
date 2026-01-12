# Code Coverage Report

**Date:** 2026-01-12  
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

**Overall Coverage:** **72.5%** (4890 statements, 1347 missed)

---

## Executive Summary

This report provides an automated, reproducible view of code coverage after running the full test suite.

### Coverage Breakdown

**Overall Statistics:**
- **Statements:** 4890
- **Covered:** 3543
- **Missing:** 1347
- **Coverage:** 72.5%


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
- **Coverage:** 0.0%
- **Statements:** 442
- **Covered:** 0
- **Missing:** 442
- **Status:** ❌

### Infrastructure Layer
- **Coverage:** 77.7%
- **Statements:** 2383
- **Covered:** 1851
- **Missing:** 532
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
- **Last Updated**: 2026-01-12T14:10:42.912826

---
