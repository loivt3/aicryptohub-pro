"""
Monitoring and metrics service for AI Hub AI Engine
Provides Prometheus metrics and health check dashboard
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Metrics storage (in-memory for simplicity)
_metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_failed": 0,
    "analysis_total": 0,
    "analysis_success": 0,
    "analysis_failed": 0,
    "analysis_duration_seconds": [],
    "db_queries_total": 0,
    "db_query_duration_seconds": [],
    "last_analysis_time": None,
    "coins_analyzed": 0,
    "uptime_start": time.time(),
}


def increment_counter(name: str, value: int = 1):
    """Increment a counter metric"""
    if name in _metrics:
        _metrics[name] += value


def record_duration(name: str, duration: float):
    """Record a duration metric"""
    key = f"{name}_duration_seconds"
    if key in _metrics:
        _metrics[key].append(duration)
        # Keep only last 1000 samples
        if len(_metrics[key]) > 1000:
            _metrics[key] = _metrics[key][-1000:]


def set_gauge(name: str, value: Any):
    """Set a gauge metric"""
    _metrics[name] = value


def track_duration(metric_name: str):
    """Decorator to track function duration"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                increment_counter(f"{metric_name}_success")
                return result
            except Exception as e:
                increment_counter(f"{metric_name}_failed")
                raise
            finally:
                duration = time.time() - start
                record_duration(metric_name, duration)
                increment_counter(f"{metric_name}_total")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                increment_counter(f"{metric_name}_success")
                return result
            except Exception as e:
                increment_counter(f"{metric_name}_failed")
                raise
            finally:
                duration = time.time() - start
                record_duration(metric_name, duration)
                increment_counter(f"{metric_name}_total")
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def get_metrics() -> Dict[str, Any]:
    """Get all metrics"""
    uptime = time.time() - _metrics["uptime_start"]
    
    # Calculate averages for durations
    avg_analysis = 0
    if _metrics["analysis_duration_seconds"]:
        avg_analysis = sum(_metrics["analysis_duration_seconds"]) / len(_metrics["analysis_duration_seconds"])
    
    avg_db = 0
    if _metrics["db_query_duration_seconds"]:
        avg_db = sum(_metrics["db_query_duration_seconds"]) / len(_metrics["db_query_duration_seconds"])
    
    return {
        "uptime_seconds": round(uptime, 2),
        "requests": {
            "total": _metrics["requests_total"],
            "success": _metrics["requests_success"],
            "failed": _metrics["requests_failed"],
            "success_rate": round(_metrics["requests_success"] / max(_metrics["requests_total"], 1) * 100, 2),
        },
        "analysis": {
            "total": _metrics["analysis_total"],
            "success": _metrics["analysis_success"],
            "failed": _metrics["analysis_failed"],
            "avg_duration_seconds": round(avg_analysis, 3),
            "last_run": _metrics["last_analysis_time"],
            "coins_analyzed": _metrics["coins_analyzed"],
        },
        "database": {
            "queries_total": _metrics["db_queries_total"],
            "avg_query_duration_seconds": round(avg_db, 4),
        },
    }


def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus format"""
    m = get_metrics()
    
    lines = [
        "# HELP aihub_uptime_seconds Service uptime in seconds",
        "# TYPE aihub_uptime_seconds gauge",
        f"aihub_uptime_seconds {m['uptime_seconds']}",
        "",
        "# HELP aihub_requests_total Total HTTP requests",
        "# TYPE aihub_requests_total counter",
        f"aihub_requests_total {m['requests']['total']}",
        f"aihub_requests_success_total {m['requests']['success']}",
        f"aihub_requests_failed_total {m['requests']['failed']}",
        "",
        "# HELP aihub_analysis_total Total analysis jobs",
        "# TYPE aihub_analysis_total counter",
        f"aihub_analysis_total {m['analysis']['total']}",
        f"aihub_analysis_success_total {m['analysis']['success']}",
        f"aihub_analysis_failed_total {m['analysis']['failed']}",
        "",
        "# HELP aihub_analysis_duration_seconds Average analysis duration",
        "# TYPE aihub_analysis_duration_seconds gauge",
        f"aihub_analysis_duration_seconds {m['analysis']['avg_duration_seconds']}",
        "",
        "# HELP aihub_coins_analyzed Total coins analyzed",
        "# TYPE aihub_coins_analyzed gauge",
        f"aihub_coins_analyzed {m['analysis']['coins_analyzed']}",
    ]
    
    return "\n".join(lines)


def get_health_dashboard() -> Dict[str, Any]:
    """Get comprehensive health dashboard data"""
    m = get_metrics()
    
    # Calculate health score (0-100)
    health_score = 100
    
    # Deduct for failures
    if m["requests"]["total"] > 0:
        failure_rate = m["requests"]["failed"] / m["requests"]["total"]
        health_score -= min(failure_rate * 100, 50)
    
    # Deduct for slow queries
    if m["database"]["avg_query_duration_seconds"] > 1.0:
        health_score -= 20
    
    # Deduct for slow analysis
    if m["analysis"]["avg_duration_seconds"] > 30:
        health_score -= 20
    
    status = "healthy"
    if health_score < 70:
        status = "degraded"
    if health_score < 50:
        status = "unhealthy"
    
    return {
        "status": status,
        "health_score": round(max(0, health_score), 1),
        "timestamp": datetime.now().isoformat(),
        "metrics": m,
        "alerts": _generate_alerts(m),
    }


def _generate_alerts(m: Dict[str, Any]) -> list:
    """Generate alerts based on metrics"""
    alerts = []
    
    if m["requests"]["failed"] > 10:
        alerts.append({
            "level": "warning",
            "message": f"High failure rate: {m['requests']['failed']} failed requests",
        })
    
    if m["analysis"]["avg_duration_seconds"] > 30:
        alerts.append({
            "level": "warning", 
            "message": f"Slow analysis: {m['analysis']['avg_duration_seconds']:.1f}s average",
        })
    
    if m["database"]["avg_query_duration_seconds"] > 1.0:
        alerts.append({
            "level": "warning",
            "message": f"Slow database: {m['database']['avg_query_duration_seconds']:.2f}s average",
        })
    
    return alerts
