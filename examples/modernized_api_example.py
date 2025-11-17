"""
Demonstration of AlgBench's modernized API features.

This example shows how the new decorator and context manager APIs
make benchmarking more Pythonic and require less boilerplate.
"""

import networkx as nx
from algbench import Benchmark


def example_1_context_manager():
    """Example 1: Using Benchmark as a context manager with auto-compression."""
    print("=" * 60)
    print("Example 1: Context Manager with Auto-Compression")
    print("=" * 60)

    # Context manager automatically handles resource cleanup
    # and compression when auto_compress=True
    with Benchmark("./example_context_mgr", auto_compress=True) as bench:

        def compute_factorial(n: int) -> dict:
            """Simple factorial computation."""
            result = 1
            for i in range(1, n + 1):
                result *= i
            return {"factorial": result, "input": n}

        # Add experiments to benchmark
        for i in range(1, 6):
            bench.add(compute_factorial, i)

        print(f"\nBenchmark has {len(bench)} entries")
        print(f"Benchmark location: {bench}")

    # Automatically compressed on exit!
    print("\n✓ Benchmark automatically compressed on context exit\n")

    # Cleanup
    bench.delete()


def example_2_decorator_api():
    """Example 2: Using the @experiment decorator."""
    print("=" * 60)
    print("Example 2: Decorator API")
    print("=" * 60)

    bench = Benchmark("./example_decorator")

    # Decorator automatically tracks function calls
    @bench.experiment
    def fibonacci(n: int) -> dict:
        """Compute nth Fibonacci number."""
        if n <= 1:
            return {"result": n, "n": n}
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return {"result": b, "n": n}

    print("\nCalling fibonacci with decorator:")

    # Just call the function normally - it's automatically tracked!
    for i in range(1, 8):
        result = fibonacci(i)
        print(f"  fibonacci({i}) = {result['result']}")

    print(f"\nBenchmark has {len(bench)} entries")

    # Calling again with same args doesn't re-record (but still executes)
    print("\nCalling fibonacci(5) again (already recorded):")
    result = fibonacci(5)
    print(f"  Result: {result['result']}")
    print(f"  Benchmark still has {len(bench)} entries (not duplicated)")

    bench.delete()


def example_3_decorator_with_parameters():
    """Example 3: Decorator with name and tags."""
    print("=" * 60)
    print("Example 3: Decorator with Parameters")
    print("=" * 60)

    bench = Benchmark("./example_decorator_params")

    # Decorator with custom name and tags for organization
    @bench.experiment(name="graph_coloring", tags=["greedy", "heuristic"])
    def color_graph(n_nodes: int, strategy: str, _graph: nx.Graph = None) -> dict:
        """Color a graph using greedy algorithm."""
        if _graph is None:
            # Generate random graph
            _graph = nx.gnp_random_graph(n_nodes, 0.3, seed=n_nodes)

        coloring = nx.coloring.greedy_color(_graph, strategy=strategy)
        n_colors = max(coloring.values()) + 1

        return {
            "n_nodes": n_nodes,
            "n_colors": n_colors,
            "strategy": strategy
        }

    print("\nTesting different graph coloring strategies:")

    strategies = ["largest_first", "smallest_last", "random_sequential"]

    for n in [10, 20]:
        graph = nx.gnp_random_graph(n, 0.3, seed=n)
        for strategy in strategies:
            result = color_graph(n, strategy, _graph=graph)
            print(f"  {n} nodes, {strategy}: {result['n_colors']} colors")

    print(f"\nBenchmark has {len(bench)} entries")

    bench.delete()


def example_4_combined():
    """Example 4: Combining context manager and decorator."""
    print("=" * 60)
    print("Example 4: Context Manager + Decorator Combined")
    print("=" * 60)

    # Best of both worlds!
    with Benchmark("./example_combined", auto_compress=True) as bench:

        @bench.experiment(name="prime_check")
        def is_prime(n: int) -> dict:
            """Check if number is prime."""
            if n < 2:
                return {"n": n, "is_prime": False}
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return {"n": n, "is_prime": False}
            return {"n": n, "is_prime": True}

        print("\nChecking primes from 1 to 20:")
        primes = []
        for i in range(1, 21):
            result = is_prime(i)
            if result["is_prime"]:
                primes.append(i)

        print(f"  Primes found: {primes}")
        print(f"  Benchmark has {len(bench)} entries")

    # Automatically compressed and cleaned up!
    print("\n✓ Context manager handled cleanup and compression\n")


def comparison_old_vs_new():
    """Show side-by-side comparison of old vs new API."""
    print("=" * 60)
    print("API Comparison: Old vs New")
    print("=" * 60)

    print("\n--- OLD API ---")
    print("""
    benchmark = Benchmark("./data")

    def my_experiment(param1, param2):
        result = algorithm(param1, param2)
        return {"result": result}

    for p1 in params1:
        for p2 in params2:
            benchmark.add(my_experiment, p1, p2)

    benchmark.compress()  # Don't forget!
    """)

    print("\n--- NEW API (with decorator + context manager) ---")
    print("""
    with Benchmark("./data", auto_compress=True) as bench:

        @bench.experiment
        def my_experiment(param1, param2):
            result = algorithm(param1, param2)
            return {"result": result}

        for p1 in params1:
            for p2 in params2:
                my_experiment(p1, p2)  # Just call it!

    # Automatically compressed on exit!
    """)

    print("\nBenefits:")
    print("  ✓ More Pythonic - uses standard decorators and context managers")
    print("  ✓ Less boilerplate - no manual compress() needed")
    print("  ✓ Cleaner code - just call the function naturally")
    print("  ✓ Backward compatible - old API still works!\n")


if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print("AlgBench Modernized API Examples")
    print("=" * 60)
    print()

    example_1_context_manager()
    example_2_decorator_api()
    example_3_decorator_with_parameters()
    example_4_combined()
    comparison_old_vs_new()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
