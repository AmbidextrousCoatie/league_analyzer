"""
Benchmark Write Operations for CSV Repositories

Measures performance of write operations (add, update, delete) for CSV repositories.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import time
from uuid import uuid4
from datetime import datetime, timedelta
import pandas as pd
from domain.entities.event import Event
from domain.value_objects.event_status import EventStatus
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository


async def benchmark_add_operations(repo: PandasEventRepository, num_events: int):
    """Benchmark adding events."""
    league_season_id = uuid4()
    events = []
    
    start_time = time.perf_counter()
    
    for i in range(num_events):
        event = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=i + 1,
            date=datetime(2024, 1, 15) + timedelta(days=i),
            venue_id=f"venue-{i % 5}",
            status=EventStatus.SCHEDULED
        )
        await repo.add(event)
        events.append(event)
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    return {
        'operation': 'add',
        'count': num_events,
        'elapsed_time': elapsed,
        'avg_time_per_op': elapsed / num_events,
        'ops_per_second': num_events / elapsed
    }


async def benchmark_update_operations(repo: PandasEventRepository, events: list):
    """Benchmark updating events."""
    start_time = time.perf_counter()
    
    for event in events:
        event.update_status(EventStatus.IN_PROGRESS)
        await repo.update(event)
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    return {
        'operation': 'update',
        'count': len(events),
        'elapsed_time': elapsed,
        'avg_time_per_op': elapsed / len(events),
        'ops_per_second': len(events) / elapsed
    }


async def benchmark_delete_operations(repo: PandasEventRepository, events: list):
    """Benchmark deleting events."""
    start_time = time.perf_counter()
    
    for event in events:
        await repo.delete(event.id)
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    return {
        'operation': 'delete',
        'count': len(events),
        'elapsed_time': elapsed,
        'avg_time_per_op': elapsed / len(events),
        'ops_per_second': len(events) / elapsed
    }


async def benchmark_batch_add(repo: PandasEventRepository, num_events: int):
    """Benchmark batch adding (load all, add all, save once)."""
    league_season_id = uuid4()
    events = []
    
    # Create all events first
    for i in range(num_events):
        event = Event(
            id=uuid4(),
            league_season_id=league_season_id,
            event_type="league",
            league_week=i + 1,
            date=datetime(2024, 1, 15) + timedelta(days=i),
            venue_id=f"venue-{i % 5}",
            status=EventStatus.SCHEDULED
        )
        events.append(event)
    
    # Batch add (simulate - would need batch method)
    start_time = time.perf_counter()
    
    for event in events:
        await repo.add(event)
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    return {
        'operation': 'batch_add',
        'count': num_events,
        'elapsed_time': elapsed,
        'avg_time_per_op': elapsed / num_events,
        'ops_per_second': num_events / elapsed
    }


async def main():
    """Run benchmarks."""
    print("=" * 70)
    print("CSV Repository Write Operations Benchmark")
    print("=" * 70)
    print()
    
    # Create temporary CSV file
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "event.csv"
        
        # Initialize empty CSV
        df = pd.DataFrame(columns=[
            'id', 'league_season_id', 'event_type', 'league_week', 'tournament_stage',
            'date', 'venue_id', 'oil_pattern_id', 'status', 'disqualification_reason', 'notes'
        ])
        df.to_csv(csv_path, index=False)
        
        # Create repository
        adapter = PandasDataAdapter(csv_path)
        mapper = PandasEventMapper()
        repo = PandasEventRepository(adapter, mapper)
        
        # Test sizes
        test_sizes = [10, 50, 100, 500, 1000]
        
        results = []
        
        for size in test_sizes:
            print(f"\nTesting with {size} events...")
            print("-" * 70)
            
            # Reset CSV
            df.to_csv(csv_path, index=False)
            
            # Benchmark ADD
            add_result = await benchmark_add_operations(repo, size)
            results.append(add_result)
            print(f"ADD:     {add_result['count']:5d} ops | "
                  f"{add_result['elapsed_time']:6.3f}s | "
                  f"{add_result['avg_time_per_op']*1000:6.2f}ms/op | "
                  f"{add_result['ops_per_second']:6.1f} ops/s")
            
            # Get events for update/delete
            all_events = await repo.get_all()
            
            # Benchmark UPDATE
            update_result = await benchmark_update_operations(repo, all_events)
            results.append(update_result)
            print(f"UPDATE:  {update_result['count']:5d} ops | "
                  f"{update_result['elapsed_time']:6.3f}s | "
                  f"{update_result['avg_time_per_op']*1000:6.2f}ms/op | "
                  f"{update_result['ops_per_second']:6.1f} ops/s")
            
            # Benchmark DELETE
            delete_result = await benchmark_delete_operations(repo, all_events)
            results.append(delete_result)
            print(f"DELETE:  {delete_result['count']:5d} ops | "
                  f"{delete_result['elapsed_time']:6.3f}s | "
                  f"{delete_result['avg_time_per_op']*1000:6.2f}ms/op | "
                  f"{delete_result['ops_per_second']:6.1f} ops/s")
        
        # Summary
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print(f"{'Operation':<12} {'Count':>8} {'Total Time':>12} {'Avg/Op':>12} {'Ops/Sec':>12}")
        print("-" * 70)
        
        for result in results:
            print(f"{result['operation']:<12} {result['count']:>8} "
                  f"{result['elapsed_time']:>11.3f}s "
                  f"{result['avg_time_per_op']*1000:>11.2f}ms "
                  f"{result['ops_per_second']:>11.1f}")
        
        print("\n" + "=" * 70)
        print("Analysis")
        print("=" * 70)
        
        # Find worst case
        worst_add = max([r for r in results if r['operation'] == 'add'], 
                       key=lambda x: x['avg_time_per_op'])
        worst_update = max([r for r in results if r['operation'] == 'update'], 
                          key=lambda x: x['avg_time_per_op'])
        worst_delete = max([r for r in results if r['operation'] == 'delete'], 
                          key=lambda x: x['avg_time_per_op'])
        
        print(f"\nWorst case ADD (1000 events):    {worst_add['avg_time_per_op']*1000:.2f}ms per operation")
        print(f"Worst case UPDATE (1000 events):  {worst_update['avg_time_per_op']*1000:.2f}ms per operation")
        print(f"Worst case DELETE (1000 events):  {worst_delete['avg_time_per_op']*1000:.2f}ms per operation")
        
        # Estimate for 200x scale (21 MB)
        estimated_events_200x = 10 * 200  # Rough estimate: 10 events now, 2000 at 200x
        estimated_add_time = worst_add['avg_time_per_op'] * estimated_events_200x
        estimated_update_time = worst_update['avg_time_per_op'] * estimated_events_200x
        estimated_delete_time = worst_delete['avg_time_per_op'] * estimated_events_200x
        
        print(f"\nEstimated for 200x scale (~2000 events):")
        print(f"  ADD:    {estimated_add_time:.2f}s ({estimated_add_time/60:.1f} minutes)")
        print(f"  UPDATE: {estimated_update_time:.2f}s ({estimated_update_time/60:.1f} minutes)")
        print(f"  DELETE: {estimated_delete_time:.2f}s ({estimated_delete_time/60:.1f} minutes)")


if __name__ == "__main__":
    asyncio.run(main())

