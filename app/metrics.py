from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "shipping_requests_total",
    "Total shipping requests"
)

REQUEST_LATENCY = Histogram(
    "shipping_request_latency_seconds",
    "Shipping request latency"
)

ERROR_COUNT = Counter(
    "shipping_errors_total",
    "Shipping errors"
)
