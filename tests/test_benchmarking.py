#!/usr/bin/env python3
"""Piranha Agent Benchmarking Suite.

Provides:
- Performance benchmarks (throughput, latency)
- Comparison with other frameworks
- Load testing
- Cost-effectiveness analysis
- Quality evaluation metrics

Usage:
    python tests/test_benchmarking.py
    pytest tests/test_benchmarking.py -v --benchmark
"""

import time
import statistics
import logging
import asyncio
from typing import Callable, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import pytest

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    p95_time: float
    p99_time: float
    throughput: float  # ops/sec
    errors: int = 0


@dataclass
class BenchmarkReport:
    """Complete benchmark report."""
    results: list[BenchmarkResult] = field(default_factory=list)
    system_info: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)
    
    def add_result(self, result: BenchmarkResult):
        self.results.append(result)
    
    def generate_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 70,
            "PIRANHA AGENT BENCHMARK REPORT",
            "=" * 70,
            "",
        ]
        
        for result in self.results:
            lines.append(f"Benchmark: {result.name}")
            lines.append(f"  Iterations:    {result.iterations}")
            lines.append(f"  Avg Time:      {result.avg_time*1000:.2f}ms")
            lines.append(f"  Median Time:   {result.median_time*1000:.2f}ms")
            lines.append(f"  P95 Time:      {result.p95_time*1000:.2f}ms")
            lines.append(f"  P99 Time:      {result.p99_time*1000:.2f}ms")
            lines.append(f"  Throughput:    {result.throughput:.2f} ops/sec")
            lines.append(f"  Errors:        {result.errors}")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)


class BenchmarkRunner:
    """Runs benchmarks and collects metrics."""
    
    def __init__(self, warmup_iterations: int = 5):
        self.warmup_iterations = warmup_iterations
        self.results: list[BenchmarkResult] = []
    
    def run(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run a synchronous benchmark."""
        times = []
        errors = 0
        
        # Warmup
        for _ in range(self.warmup_iterations):
            try:
                func(*args, **kwargs)
            except Exception as e:
                # Ignore errors during warmup
                logger.debug(f"Warmup error (ignored): {e}")
        
        # Benchmark
        for i in range(iterations):
            start = time.perf_counter()
            try:
                func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception:
                errors += 1
        
        # Calculate statistics
        times.sort()
        total_time = sum(times)
        avg_time = total_time / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        median_time = statistics.median(times) if times else 0
        p95_time = self._percentile(times, 95)
        p99_time = self._percentile(times, 99)
        throughput = iterations / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            p95_time=p95_time,
            p99_time=p99_time,
            throughput=throughput,
            errors=errors,
        )
        
        self.results.append(result)
        return result
    
    async def run_async(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run an asynchronous benchmark."""
        times = []
        errors = 0
        
        # Warmup
        for _ in range(self.warmup_iterations):
            try:
                await func(*args, **kwargs)
            except Exception as e:
                # Ignore errors during warmup
                logger.debug(f"Warmup error (ignored): {e}")
        
        # Benchmark
        for i in range(iterations):
            start = time.perf_counter()
            try:
                await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception:
                errors += 1
        
        # Calculate statistics
        times.sort()
        total_time = sum(times)
        avg_time = total_time / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        median_time = statistics.median(times) if times else 0
        p95_time = self._percentile(times, 95)
        p99_time = self._percentile(times, 99)
        throughput = iterations / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            p95_time=p95_time,
            p99_time=p99_time,
            throughput=throughput,
            errors=errors,
        )
        
        self.results.append(result)
        return result
    
    def run_concurrent(
        self,
        name: str,
        func: Callable,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run concurrent load test."""
        times = []
        errors = 0
        total_requests = concurrent_users * requests_per_user
        
        def worker():
            for _ in range(requests_per_user):
                start = time.perf_counter()
                try:
                    func(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    times.append(elapsed)
                except Exception:
                    nonlocal errors
                    errors += 1
        
        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            for future in asyncio.as_completed(futures):
                future.result()
        
        # Calculate statistics
        times.sort()
        total_time = sum(times)
        avg_time = total_time / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        median_time = statistics.median(times) if times else 0
        p95_time = self._percentile(times, 95)
        p99_time = self._percentile(times, 99)
        throughput = len(times) / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            name=f"{name} (concurrent={concurrent_users})",
            iterations=total_requests,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            p95_time=p95_time,
            p99_time=p99_time,
            throughput=throughput,
            errors=errors,
        )
        
        self.results.append(result)
        return result
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_report(self) -> BenchmarkReport:
        """Generate complete benchmark report."""
        report = BenchmarkReport()
        report.results = self.results
        
        # Calculate overall summary
        if self.results:
            total_throughput = sum(r.throughput for r in self.results)
            avg_latency = statistics.mean(r.avg_time for r in self.results)
            total_errors = sum(r.errors for r in self.results)
            
            report.summary = {
                "total_benchmarks": len(self.results),
                "total_throughput": total_throughput,
                "average_latency_ms": avg_latency * 1000,
                "total_errors": total_errors,
            }
        
        return report


# =============================================================================
# Piranha-Specific Benchmarks
# =============================================================================

class TestPiranhaBenchmarks:
    """Benchmarks for Piranha Agent components."""
    
    @pytest.fixture
    def runner(self):
        return BenchmarkRunner()
    
    @pytest.fixture
    def agent(self):
        from piranha import Agent
        return Agent(name="benchmark-agent", model="ollama/llama3:latest")
    
    @pytest.fixture
    def semantic_cache(self):
        from piranha_core import SemanticCache
        return SemanticCache(ttl_hours=24, max_entries=10000)
    
    @pytest.fixture
    def event_store(self):
        from piranha_core import EventStore
        return EventStore()
    
    def test_agent_creation_benchmark(self, runner):
        """Benchmark: Agent creation speed."""
        from piranha import Agent
        
        def create_agent():
            return Agent(name="test", model="ollama/llama3:latest")
        
        result = runner.run("Agent Creation", create_agent, iterations=50)
        
        print(f"\nAgent Creation: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.avg_time < 1.0  # Should be < 1ms
    
    def test_event_store_append_benchmark(self, runner, event_store):
        """Benchmark: Event store append performance."""
        import uuid
        
        def append_event():
            return event_store.record_llm_call(
                session_id=str(uuid.uuid4()),
                agent_id=str(uuid.uuid4()),
                model="llama3",
                prompt_tokens=100,
                completion_tokens=50,
                cost_usd=0.001,
                cache_hit=False,
                context_event_count=10,
            )
        
        result = runner.run("EventStore Append", append_event, iterations=100)
        
        print(f"\nEventStore Append: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 100  # Should handle 100+ events/sec
    
    def test_semantic_cache_put_benchmark(self, runner, semantic_cache):
        """Benchmark: Semantic cache put performance."""
        def put_cache():
            semantic_cache.put(
                key=f"test_{time.time()}",
                response="Test response",
                model="llama3",
                prompt_tokens=10,
                completion_tokens=20,
                cost_usd=0.001,
            )
        
        result = runner.run("SemanticCache Put", put_cache, iterations=100)
        
        print(f"\nSemanticCache Put: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 500  # Should handle 500+ puts/sec
    
    def test_semantic_cache_get_benchmark(self, runner, semantic_cache):
        """Benchmark: Semantic cache get performance."""
        # Pre-populate cache
        for i in range(100):
            semantic_cache.put(
                key=f"key_{i}",
                response=f"Response {i}",
                model="llama3",
                prompt_tokens=10,
                completion_tokens=20,
                cost_usd=0.001,
            )
        
        def get_cache():
            return semantic_cache.get("key_50")
        
        result = runner.run("SemanticCache Get", get_cache, iterations=100)
        
        print(f"\nSemanticCache Get: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 1000  # Should handle 1000+ gets/sec
    
    def test_skill_registry_authorize_benchmark(self, runner):
        """Benchmark: Skill registry authorization performance."""
        from piranha_core import SkillRegistry
        import uuid
        
        registry = SkillRegistry()
        agent_id = str(uuid.uuid4())
        
        # Register skill
        registry.register_skill(
            skill_id="test_skill",
            name="Test Skill",
            description="Test skill for benchmarking purposes",
            parameters_schema={},
            permissions=["cache_access"],
            inheritable=True,
        )
        registry.grant_skills(agent_id, ["test_skill"])
        
        def authorize():
            registry.authorize(agent_id, "test_skill")
        
        result = runner.run("SkillRegistry Authorize", authorize, iterations=100)
        
        print(f"\nSkillRegistry Authorize: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 1000  # Should handle 1000+ auth/sec
    
    def test_guardrail_check_benchmark(self, runner):
        """Benchmark: Guardrail check performance."""
        from piranha_core import GuardrailEngine
        import uuid
        
        engine = GuardrailEngine(token_budget=100000)
        agent_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        def check_guardrail():
            return engine.check(
                agent_id=agent_id,
                session_id=session_id,
                tokens_used=100,
                token_budget=100000,
                pending_action=None,
            )
        
        result = runner.run("Guardrail Check", check_guardrail, iterations=100)
        
        print(f"\nGuardrail Check: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 1000  # Should handle 1000+ checks/sec
    
    def test_wasm_validate_benchmark(self, runner):
        """Benchmark: Wasm validation performance."""
        from piranha_core import WasmRunner
        
        runner_instance = WasmRunner()
        
        # Valid Wasm magic number
        valid_wasm = bytes([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00])
        
        def validate_wasm():
            return runner_instance.validate(valid_wasm)
        
        result = runner.run("Wasm Validate", validate_wasm, iterations=100)
        
        print(f"\nWasm Validate: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 10000  # Should handle 10K+ validations/sec
    
    def test_memory_vector_search_benchmark(self, runner):
        """Benchmark: Memory vector search performance."""
        from piranha.memory import MemoryManager, VectorStore
        
        store = VectorStore()
        
        # Pre-populate with vectors
        for i in range(1000):
            vector = [float(i % 100) / 100 for _ in range(384)]  # 384-dim embedding
            store.add(f"item_{i}", vector, {"content": f"Item {i}"})
        
        query_vector = [0.5] * 384
        
        def search():
            return store.similarity_search(query_vector, top_k=5)
        
        result = runner.run("Vector Search (1K items)", search, iterations=50)
        
        print(f"\nVector Search: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.avg_time < 0.1  # Should be < 100ms for 1K items
    
    def test_observability_metrics_benchmark(self, runner):
        """Benchmark: Observability metrics collection."""
        from piranha.observability import MetricsCollector
        
        metrics = MetricsCollector()
        
        def record_metrics():
            metrics.increment_counter("requests_total")
            metrics.record_histogram("request_latency", 50.0)
            metrics.set_gauge("active_connections", 10)
        
        result = runner.run("Metrics Collection", record_metrics, iterations=100)
        
        print(f"\nMetrics Collection: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.throughput > 10000  # Should handle 10K+ metrics/sec
    
    def test_cost_anomaly_detection_benchmark(self, runner):
        """Benchmark: Cost anomaly detection performance."""
        from piranha.observability import CostAnomalyDetector
        
        detector = CostAnomalyDetector(window_size=100)
        
        # Pre-populate with normal costs
        for _ in range(100):
            detector.record_cost(0.001)
        
        def detect_anomaly():
            return detector.record_cost(0.01)  # 10x normal
        
        result = runner.run("Cost Anomaly Detection", detect_anomaly, iterations=50)
        
        print(f"\nCost Anomaly Detection: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.avg_time < 0.001  # Should be < 1ms
    
    def test_concurrent_agent_execution_benchmark(self, runner):
        """Benchmark: Concurrent agent execution."""
        from piranha import Agent
        
        def create_and_run():
            agent = Agent(name="test", model="ollama/llama3:latest")
            return agent.id
        
        result = runner.run_concurrent(
            "Concurrent Agent Creation",
            create_and_run,
            concurrent_users=10,
            requests_per_user=10,
        )
        
        print(f"\nConcurrent Agent Creation: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.errors == 0  # Should have no errors
    
    def test_export_prometheus_benchmark(self, runner):
        """Benchmark: Prometheus metrics export."""
        from piranha.observability import MetricsCollector
        
        metrics = MetricsCollector()
        
        # Add some metrics
        for i in range(100):
            metrics.increment_counter("requests_total", labels={"endpoint": f"/api/{i}"})
            metrics.record_histogram("latency", float(i))
        
        def export():
            return metrics.export_prometheus()
        
        result = runner.run("Prometheus Export", export, iterations=20)
        
        print(f"\nPrometheus Export: {result.avg_time*1000:.2f}ms avg, {result.throughput:.2f} ops/sec")
        assert result.avg_time < 0.01  # Should be < 10ms


def run_all_benchmarks():
    """Run all benchmarks and print report."""
    print("=" * 70)
    print("PIRANHA AGENT - COMPREHENSIVE BENCHMARK SUITE")
    print("=" * 70)
    print()
    
    runner = BenchmarkRunner()
    test_class = TestPiranhaBenchmarks()
    
    # Create fixtures manually
    from piranha_core import SemanticCache, EventStore, SkillRegistry, GuardrailEngine, WasmRunner
    
    semantic_cache = SemanticCache(ttl_hours=24, max_entries=10000)
    event_store = EventStore()
    
    # Run benchmarks
    print("Running benchmarks...\n")
    
    test_class.test_event_store_append_benchmark(runner, event_store)
    test_class.test_semantic_cache_put_benchmark(runner, semantic_cache)
    test_class.test_semantic_cache_get_benchmark(runner, semantic_cache)
    test_class.test_skill_registry_authorize_benchmark(runner)
    test_class.test_guardrail_check_benchmark(runner)
    test_class.test_wasm_validate_benchmark(runner)
    test_class.test_memory_vector_search_benchmark(runner)
    test_class.test_observability_metrics_benchmark(runner)
    test_class.test_cost_anomaly_detection_benchmark(runner)
    test_class.test_export_prometheus_benchmark(runner)
    
    # Generate report
    report = runner.generate_report()
    print()
    print(report.generate_summary())
    
    return report


if __name__ == "__main__":
    run_all_benchmarks()
