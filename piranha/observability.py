"""Observability module for Piranha Agent.

Provides:
- OpenTelemetry distributed tracing
- Metrics collection (Prometheus format)
- Alerting (Slack, PagerDuty)
- Cost anomaly detection
"""

from __future__ import annotations

import statistics
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: datetime
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class AlertConfig:
    """Configuration for an alert."""
    name: str
    threshold: float
    comparison: str  # "gt", "lt", "eq"
    cooldown_seconds: int = 300
    channels: list[str] = field(default_factory=list)


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self):
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
    
    def increment_counter(self, name: str, value: int = 1, labels: dict | None = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self._counters[key] += value
    
    def set_gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
        self._metrics[name].append(MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
        ))
    
    def record_histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        """Record a histogram value."""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        self._metrics[name].append(MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
        ))
    
    def get_counter(self, name: str, labels: dict | None = None) -> int:
        """Get counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)
    
    def get_gauge(self, name: str, labels: dict | None = None) -> float | None:
        """Get gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: dict | None = None) -> dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
            "p95": self._percentile(values, 95) if len(values) >= 20 else max(values),
            "p99": self._percentile(values, 99) if len(values) >= 100 else max(values),
        }
    
    def get_metric_history(self, name: str, minutes: int = 60) -> list[MetricPoint]:
        """Get metric history for the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [p for p in self._metrics[name] if p.timestamp > cutoff]
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Counters
        for key, value in self._counters.items():
            name = key.split("{")[0] if "{" in key else key
            lines.append(f"# TYPE {name} counter")
            lines.append(f'{key} {value}')
        
        # Gauges
        for key, value in self._gauges.items():
            name = key.split("{")[0] if "{" in key else key
            lines.append(f"# TYPE {name} gauge")
            lines.append(f'{key} {value}')
        
        # Histograms
        for key in self._histograms:
            name = key.split("{")[0] if "{" in key else key
            stats = self.get_histogram_stats(name, self._parse_labels(key))
            if stats:
                lines.append(f"# TYPE {name} histogram")
                lines.append(f'{key}_count {stats["count"]}')
                lines.append(f'{key}_sum {stats["sum"]}')
        
        return "\n".join(lines)
    
    def _make_key(self, name: str, labels: dict | None) -> str:
        """Create a metric key with labels."""
        if not labels:
            return name
        
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f'{name}{{{label_str}}}'
    
    def _parse_labels(self, key: str) -> dict[str, str]:
        """Parse labels from a metric key."""
        if "{" not in key:
            return {}
        
        labels_str = key[key.index("{")+1:key.index("}")]
        labels = {}
        for pair in labels_str.split(","):
            k, v = pair.split("=")
            labels[k.strip()] = v.strip('"')
        return labels
    
    def _percentile(self, values: list[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self._configs: dict[str, AlertConfig] = {}
        self._last_alert: dict[str, datetime] = {}
        self._handlers: dict[str, Callable] = {}
        self._register_default_handlers()
    
    def register_config(self, config: AlertConfig) -> None:
        """Register an alert configuration."""
        self._configs[config.name] = config
    
    def register_handler(self, channel: str, handler: Callable) -> None:
        """Register a notification handler for a channel."""
        self._handlers[channel] = handler
    
    def check_alerts(self, metrics: MetricsCollector) -> list[str]:
        """Check all alerts and trigger if needed."""
        triggered = []
        now = datetime.utcnow()
        
        for name, config in self._configs.items():
            # Check cooldown
            if name in self._last_alert:
                elapsed = (now - self._last_alert[name]).total_seconds()
                if elapsed < config.cooldown_seconds:
                    continue
            
            # Get metric value
            metric_value = self._get_metric_value(metrics, name)
            if metric_value is None:
                continue
            
            # Check threshold
            triggered_alert = self._check_threshold(metric_value, config)
            
            if triggered_alert:
                self._last_alert[name] = now
                self._send_alerts(config, metric_value)
                triggered.append(name)
        
        return triggered
    
    def _get_metric_value(self, metrics: MetricsCollector, alert_name: str) -> float | None:
        """Get metric value for an alert."""
        # Try gauge first
        value = metrics.get_gauge(alert_name)
        if value is not None:
            return value
        
        # Try counter
        value = metrics.get_counter(alert_name)
        if value > 0:
            return float(value)
        
        # Try histogram avg
        stats = metrics.get_histogram_stats(alert_name)
        if stats:
            return stats.get("avg")
        
        return None
    
    def _check_threshold(self, value: float, config: AlertConfig) -> bool:
        """Check if value triggers alert."""
        if config.comparison == "gt":
            return value > config.threshold
        elif config.comparison == "lt":
            return value < config.threshold
        elif config.comparison == "eq":
            return value == config.threshold
        return False
    
    def _send_alerts(self, config: AlertConfig, value: float) -> None:
        """Send alerts to configured channels."""
        message = f"🚨 Alert: {config.name} = {value:.2f} (threshold: {config.comparison} {config.threshold})"
        
        for channel in config.channels:
            if channel in self._handlers:
                try:
                    self._handlers[channel](message)
                except Exception as e:
                    print(f"Failed to send alert to {channel}: {e}")
    
    def _register_default_handlers(self):
        """Register default notification handlers."""
        # Console handler (default)
        self._handlers["console"] = lambda msg: print(f"[ALERT] {msg}")
        
        # Slack handler template
        def slack_handler(message: str):
            # Would integrate with Slack API
            print(f"[Slack] {message}")
        
        self._handlers["slack"] = slack_handler
        
        # PagerDuty handler template
        def pagerduty_handler(message: str):
            # Would integrate with PagerDuty API
            print(f"[PagerDuty] {message}")
        
        self._handlers["pagerduty"] = pagerduty_handler


class CostAnomalyDetector:
    """Detects anomalies in cost patterns."""
    
    def __init__(self, window_size: int = 100, threshold_std: float = 3.0):
        self.window_size = window_size
        self.threshold_std = threshold_std
        self._cost_history: list[float] = []
        self._baseline_mean: float | None = None
        self._baseline_std: float | None = None
        self._anomalies: list[dict] = []
    
    def record_cost(self, cost: float) -> dict | None:
        """Record a cost and check for anomaly."""
        self._cost_history.append(cost)
        
        # Keep only recent history
        if len(self._cost_history) > self.window_size * 2:
            self._cost_history = self._cost_history[-self.window_size * 2:]
        
        # Need enough data for baseline
        if len(self._cost_history) < self.window_size:
            return None
        
        # Calculate baseline from older half
        baseline_data = self._cost_history[:self.window_size]
        recent_data = self._cost_history[self.window_size:]
        
        self._baseline_mean = statistics.mean(baseline_data)
        self._baseline_std = statistics.stdev(baseline_data) if len(baseline_data) > 1 else 0
        
        # Check recent costs for anomalies
        for _i, cost in enumerate(recent_data):
            if self._is_anomaly(cost):
                anomaly = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "cost": cost,
                    "baseline_mean": self._baseline_mean,
                    "baseline_std": self._baseline_std,
                    "z_score": self._calculate_z_score(cost),
                    "severity": self._calculate_severity(cost),
                }
                self._anomalies.append(anomaly)
                return anomaly
        
        return None
    
    def _is_anomaly(self, cost: float) -> bool:
        """Check if cost is anomalous."""
        if self._baseline_std == 0:
            return False
        
        z_score = self._calculate_z_score(cost)
        return abs(z_score) > self.threshold_std
    
    def _calculate_z_score(self, cost: float) -> float:
        """Calculate z-score for a cost value."""
        if self._baseline_std == 0:
            return 0
        return (cost - self._baseline_mean) / self._baseline_std
    
    def _calculate_severity(self, cost: float) -> str:
        """Calculate anomaly severity."""
        z_score = abs(self._calculate_z_score(cost))
        
        if z_score > 5:
            return "critical"
        elif z_score > 4:
            return "high"
        elif z_score > 3:
            return "medium"
        else:
            return "low"
    
    def get_anomalies(self, hours: int = 24) -> list[dict]:
        """Get recent anomalies."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        return [a for a in self._anomalies if a["timestamp"] > cutoff_str]
    
    def get_cost_stats(self) -> dict[str, float]:
        """Get cost statistics."""
        if not self._cost_history:
            return {}
        
        return {
            "current": self._cost_history[-1] if self._cost_history else 0,
            "mean": statistics.mean(self._cost_history),
            "median": statistics.median(self._cost_history),
            "std": statistics.stdev(self._cost_history) if len(self._cost_history) > 1 else 0,
            "min": min(self._cost_history),
            "max": max(self._cost_history),
            "anomaly_count": len(self.get_anomalies()),
        }


class ObservabilityManager:
    """Main observability manager combining all components."""
    
    def __init__(
        self,
        service_name: str = "piranha-agent",
        otlp_endpoint: str | None = None,
    ):
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.cost_detector = CostAnomalyDetector()
        self.tracer = None
        
        # Initialize tracing
        self._init_tracing(service_name, otlp_endpoint)
        
        # Register default alerts
        self._register_default_alerts()
    
    def _init_tracing(self, service_name: str, otlp_endpoint: str | None) -> None:
        """Initialize OpenTelemetry tracing."""
        provider = TracerProvider()
        
        if otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(service_name)
    
    def _register_default_alerts(self) -> None:
        """Register default alert configurations."""
        # High cost alert
        self.alerts.register_config(AlertConfig(
            name="cost_per_minute",
            threshold=1.0,  # $1 per minute
            comparison="gt",
            cooldown_seconds=300,
            channels=["console", "slack"],
        ))
        
        # High latency alert
        self.alerts.register_config(AlertConfig(
            name="request_latency",
            threshold=5000,  # 5 seconds
            comparison="gt",
            cooldown_seconds=60,
            channels=["console"],
        ))
        
        # Error rate alert
        self.alerts.register_config(AlertConfig(
            name="error_rate",
            threshold=0.05,  # 5% error rate
            comparison="gt",
            cooldown_seconds=300,
            channels=["console", "pagerduty"],
        ))
    
    def track_request(self, operation: str):
        """Context manager for tracking requests."""
        return RequestTracker(self, operation)
    
    def record_token_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
    ) -> None:
        """Record token usage and cost."""
        labels = {"model": model}
        
        self.metrics.increment_counter("tokens_total", prompt_tokens + completion_tokens, labels)
        self.metrics.increment_counter("prompt_tokens", prompt_tokens, labels)
        self.metrics.increment_counter("completion_tokens", completion_tokens, labels)
        self.metrics.increment_counter("cost_total", cost_usd, labels)
        
        # Check for cost anomaly
        anomaly = self.cost_detector.record_cost(cost_usd)
        if anomaly:
            print(f"⚠️ Cost anomaly detected: ${cost_usd:.4f} (z-score: {anomaly['z_score']:.2f})")
    
    def record_latency(self, operation: str, latency_ms: float, labels: dict | None = None) -> None:
        """Record request latency."""
        self.metrics.record_histogram(f"{operation}_latency", latency_ms, labels)
        self.metrics.set_gauge("request_latency", latency_ms, labels)
    
    def record_error(self, operation: str, error_type: str, labels: dict | None = None) -> None:
        """Record an error."""
        self.metrics.increment_counter("errors_total", 1, {** (labels or {}), "type": error_type})
    
    def check_alerts(self) -> list[str]:
        """Check and trigger alerts."""
        return self.alerts.check_alerts(self.metrics)
    
    def get_dashboard_data(self) -> dict[str, Any]:
        """Get data for dashboard display."""
        return {
            "metrics": {
                "tokens": self.metrics.get_histogram_stats("tokens_total"),
                "latency": self.metrics.get_histogram_stats("request_latency"),
                "errors": self.metrics.get_counter("errors_total"),
                "cost": self.cost_detector.get_cost_stats(),
            },
            "anomalies": self.cost_detector.get_anomalies(),
            "prometheus": self.metrics.export_prometheus(),
        }


class RequestTracker:
    """Context manager for tracking individual requests."""
    
    def __init__(self, manager: ObservabilityManager, operation: str):
        self.manager = manager
        self.operation = operation
        self.start_time = None
        self.span = None
    
    def __enter__(self):
        self.start_time = time.time()
        
        if self.manager.tracer:
            self.span = self.manager.tracer.start_span(self.operation)
            self.span.set_attribute("operation", self.operation)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.time() - self.start_time) * 1000
        
        self.manager.record_latency(self.operation, latency_ms)
        
        if exc_type:
            self.manager.record_error(self.operation, exc_type.__name__)
            
            if self.span:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
        else:
            if self.span:
                self.span.set_status(Status(StatusCode.OK))
        
        if self.span:
            self.span.end()
        
        # Check alerts
        self.manager.check_alerts()


# Global observability instance
_observability: ObservabilityManager | None = None


def get_observability() -> ObservabilityManager:
    """Get or create global observability manager."""
    global _observability
    if _observability is None:
        _observability = ObservabilityManager()
    return _observability


def init_observability(
    service_name: str = "piranha-agent",
    otlp_endpoint: str | None = None,
) -> ObservabilityManager:
    """Initialize global observability manager."""
    global _observability
    _observability = ObservabilityManager(service_name, otlp_endpoint)
    return _observability
