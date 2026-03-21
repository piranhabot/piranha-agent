#!/usr/bin/env python3
"""Observability Example - Tracing, Metrics, Alerting, and Cost Anomaly Detection.

This example demonstrates Piranha's Phase 8 features:
- OpenTelemetry distributed tracing
- Metrics collection (Prometheus format)
- Alerting (Slack, PagerDuty)
- Cost anomaly detection

Usage:
    python examples/09_observability.py
"""

from piranha import (
    Agent,
)


def main():
    print("=" * 70)
    print("OBSERVABILITY EXAMPLE - Tracing, Metrics, Alerting, Cost Detection")
    print("=" * 70)
    print()

    # -------------------------------------------------------------------------
    # Part 1: Initialize Observability
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 1: Initialize Observability")
    print("-" * 70)
    print()

    # Initialize with OTLP endpoint (optional - for Jaeger/Zipkin)
    # obs = init_observability(
    #     service_name="piranha-agent",
    #     otlp_endpoint="http://localhost:4317",  # Jaeger
    # )
    
    # Or use default (no tracing exporter)
    obs = get_observability()
    print(f"✓ Observability manager initialized")
    print()

    # -------------------------------------------------------------------------
    # Part 2: Register Custom Alerts
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 2: Register Custom Alerts")
    print("-" * 70)
    print()

    from piranha.observability import AlertConfig

    # High cost alert - $5 per minute
    obs.alerts.register_config(AlertConfig(
        name="high_cost_rate",
        threshold=5.0,
        comparison="gt",
        cooldown_seconds=300,
        channels=["console"],
    ))
    print("  ✓ Registered: High cost rate alert ($5/min)")

    # High error rate alert - 10%
    obs.alerts.register_config(AlertConfig(
        name="high_error_rate",
        threshold=0.10,
        comparison="gt",
        cooldown_seconds=300,
        channels=["console"],
    ))
    print("  ✓ Registered: High error rate alert (10%)")

    # Low latency alert (good performance)
    obs.alerts.register_config(AlertConfig(
        name="excellent_latency",
        threshold=100,
        comparison="lt",
        cooldown_seconds=60,
        channels=["console"],
    ))
    print("  ✓ Registered: Excellent latency alert (<100ms)")
    print()

    # -------------------------------------------------------------------------
    # Part 3: Track Requests with Tracing
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 3: Track Requests with Tracing")
    print("-" * 70)
    print()

    # Simulate some requests
    for i in range(5):
        with obs.track_request("agent_chat"):
            # Simulate work
            import time
            time.sleep(0.05)  # 50ms latency
            
            # Record metrics
            obs.record_token_usage(
                model="llama3",
                prompt_tokens=50 + i * 10,
                completion_tokens=30 + i * 5,
                cost_usd=0.001 + i * 0.0001,
            )
    
    print("  ✓ Tracked 5 agent chat requests")
    print()

    # -------------------------------------------------------------------------
    # Part 4: View Metrics
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 4: View Metrics")
    print("-" * 70)
    print()

    # Get token stats
    token_stats = obs.metrics.get_histogram_stats("tokens_total")
    print(f"  Token Usage Statistics:")
    print(f"    - Count: {token_stats.get('count', 0)}")
    print(f"    - Total: {token_stats.get('sum', 0):.0f} tokens")
    print(f"    - Average: {token_stats.get('avg', 0):.1f} tokens/request")
    print(f"    - P95: {token_stats.get('p95', 0):.1f} tokens")
    print()

    # Get latency stats
    latency_stats = obs.metrics.get_histogram_stats("agent_chat_latency")
    print(f"  Latency Statistics:")
    print(f"    - Count: {latency_stats.get('count', 0)}")
    print(f"    - Average: {latency_stats.get('avg', 0):.1f}ms")
    print(f"    - Min: {latency_stats.get('min', 0):.1f}ms")
    print(f"    - Max: {latency_stats.get('max', 0):.1f}ms")
    print(f"    - P95: {latency_stats.get('p95', 0):.1f}ms")
    print()

    # Get cost stats
    cost_stats = obs.cost_detector.get_cost_stats()
    print(f"  Cost Statistics:")
    print(f"    - Current: ${cost_stats.get('current', 0):.6f}")
    print(f"    - Mean: ${cost_stats.get('mean', 0):.6f}")
    print(f"    - Min: ${cost_stats.get('min', 0):.6f}")
    print(f"    - Max: ${cost_stats.get('max', 0):.6f}")
    print()

    # -------------------------------------------------------------------------
    # Part 5: Export Prometheus Metrics
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 5: Export Prometheus Metrics")
    print("-" * 70)
    print()

    prometheus_output = obs.metrics.export_prometheus()
    print("  Prometheus Format:")
    for line in prometheus_output.split("\n")[:10]:  # Show first 10 lines
        print(f"    {line}")
    if len(prometheus_output.split("\n")) > 10:
        print(f"    ... ({len(prometheus_output.split(chr(10))) - 10} more lines)")
    print()

    # -------------------------------------------------------------------------
    # Part 6: Cost Anomaly Detection
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 6: Cost Anomaly Detection")
    print("-" * 70)
    print()

    # Simulate normal costs
    print("  Recording normal costs...")
    for i in range(20):
        obs.cost_detector.record_cost(0.001)  # Normal: $0.001
    
    # Simulate anomaly
    print("  Recording anomalous cost...")
    anomaly = obs.cost_detector.record_cost(0.01)  # Anomaly: $0.01 (10x normal)
    
    if anomaly:
        print(f"  ⚠️  ANOMALY DETECTED!")
        print(f"      Cost: ${anomaly['cost']:.4f}")
        print(f"      Baseline: ${anomaly['baseline_mean']:.4f}")
        print(f"      Z-Score: {anomaly['z_score']:.2f}")
        print(f"      Severity: {anomaly['severity']}")
    else:
        print("  No anomaly detected (may need more data)")
    print()

    # Get all anomalies
    anomalies = obs.cost_detector.get_anomalies(hours=1)
    print(f"  Total anomalies in last hour: {len(anomalies)}")
    print()

    # -------------------------------------------------------------------------
    # Part 7: Check Alerts
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 7: Check Alerts")
    print("-" * 70)
    print()

    # Set some metrics that might trigger alerts
    obs.metrics.set_gauge("request_latency", 50)  # 50ms - should trigger excellent_latency
    obs.metrics.increment_counter("errors_total", 2)
    obs.metrics.increment_counter("tokens_total", 1000)

    # Check alerts
    triggered = obs.check_alerts()
    
    if triggered:
        print(f"  🚨 Alerts triggered: {triggered}")
    else:
        print("  ✓ No alerts triggered")
    print()

    # -------------------------------------------------------------------------
    # Part 8: Dashboard Data
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 8: Dashboard Data")
    print("-" * 70)
    print()

    dashboard = obs.get_dashboard_data()
    
    print("  Dashboard Summary:")
    print(f"    - Token stats available: {'tokens' in dashboard['metrics']}")
    print(f"    - Latency stats available: {'latency' in dashboard['metrics']}")
    print(f"    - Cost stats available: {'cost' in dashboard['metrics']}")
    print(f"    - Anomalies tracked: {len(dashboard['anomalies'])}")
    print(f"    - Prometheus export: {len(dashboard['prometheus'])} bytes")
    print()

    # -------------------------------------------------------------------------
    # Part 9: Integration with Agent
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("Part 9: Integration with Agent (Demo)")
    print("-" * 70)
    print()

    # Create agent
    agent = Agent(name="observable-agent", model="ollama/llama3:latest")
    print(f"  ✓ Created agent: {agent.name}")
    
    # Track agent execution
    with obs.track_request("agent_execution"):
        # Simulate agent work (without actual LLM call)
        obs.record_token_usage(
            model="llama3",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.002,
        )
    
    print("  ✓ Tracked agent execution")
    print()

    # Final stats
    final_stats = obs.get_dashboard_data()
    print("  Final Statistics:")
    print(f"    - Total tokens tracked: {final_stats['metrics']['tokens'].get('sum', 0):.0f}")
    print(f"    - Total cost: ${final_stats['metrics']['cost'].get('current', 0):.6f}")
    print(f"    - Anomalies detected: {final_stats['anomalies']}")
    print()

    print("=" * 70)
    print("OBSERVABILITY EXAMPLE COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Set up Jaeger/Zipkin for distributed tracing")
    print("     docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one")
    print()
    print("  2. Set up Prometheus for metrics scraping")
    print("     prometheus.yml:")
    print("       scrape_configs:")
    print("         - job_name: 'piranha'")
    print("           static_configs:")
    print("             - targets: ['localhost:8000/metrics']")
    print()
    print("  3. Set up Grafana dashboard")
    print("     Import dashboard from grafana.com/dashboards")
    print()
    print("  4. Configure Slack/PagerDuty alerts")
    print("     obs.alerts.register_handler('slack', your_slack_webhook)")
    print()


if __name__ == "__main__":
    main()
