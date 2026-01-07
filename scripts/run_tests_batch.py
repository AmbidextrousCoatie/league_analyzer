"""
Run tests in batches to avoid connection issues.

This script runs pytest on test files in smaller batches,
allowing for better resource management and avoiding timeouts.
"""

import subprocess
import sys
from pathlib import Path

# Test file groups - organized by domain/infrastructure
TEST_GROUPS = [
    # Domain - Value Objects (all passing)
    [
        "tests/domain/test_value_objects_game_result.py",
        "tests/domain/test_value_objects_handicap.py",
        "tests/domain/test_value_objects_points.py",
        "tests/domain/test_value_objects_score.py",
        "tests/domain/test_value_objects_season.py",
    ],
    # Domain - Entities (some failing)
    [
        "tests/domain/test_entities_game.py",
    ],
    [
        "tests/domain/test_entities_league.py",
    ],
    [
        "tests/domain/test_entities_player.py",
    ],
    [
        "tests/domain/test_entities_team.py",
    ],
    # Domain - Services (some failing)
    [
        "tests/domain/test_domain_services_handicap_calculator.py",
    ],
    [
        "tests/domain/test_domain_services_standings_calculator.py",
    ],
    [
        "tests/domain/test_domain_services_statistics_calculator.py",
    ],
    # Infrastructure - Repositories (new ones)
    [
        "tests/infrastructure/test_repositories_csv/test_match_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_game_result_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_position_comparison_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_match_scoring_repository.py",
    ],
    # Infrastructure - Repositories (existing)
    [
        "tests/infrastructure/test_repositories_csv/test_event_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_game_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_league_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_league_season_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_player_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_team_repository.py",
    ],
    [
        "tests/infrastructure/test_repositories_csv/test_team_season_repository.py",
    ],
]


def run_test_group(group_name: str, test_files: list[str]) -> tuple[bool, str]:
    """Run a group of test files."""
    print(f"\n{'='*80}")
    print(f"Running test group: {group_name}")
    print(f"Files: {', '.join(test_files)}")
    print(f"{'='*80}\n")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
    ] + test_files
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per group
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        print(output)
        
        if not success:
            print(f"\n❌ Group {group_name} FAILED")
        else:
            print(f"\n✅ Group {group_name} PASSED")
        
        return success, output
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  Group {group_name} TIMED OUT")
        return False, "Test group timed out after 5 minutes"
    except Exception as e:
        print(f"\n❌ Error running group {group_name}: {e}")
        return False, str(e)


def main():
    """Run all test groups."""
    print("Starting batch test execution...")
    print(f"Total groups: {len(TEST_GROUPS)}\n")
    
    results = []
    for i, test_files in enumerate(TEST_GROUPS, 1):
        group_name = f"Group {i}"
        success, output = run_test_group(group_name, test_files)
        results.append((group_name, success, output))
        
        # Small delay between groups
        import time
        time.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    for group_name, success, _ in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {group_name}")
    
    print(f"\nTotal: {len(results)} groups")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

