from functools import lru_cache
from aws_lambda_powertools import Logger, Metrics

NAMESPACE = "Conciliation"


@lru_cache(maxsize=None)
def get_logger(service: str | None = None) -> Logger:
    return Logger(service=service, log_uncaught_exceptions=True)


@lru_cache(maxsize=None)
def get_metrics(service: str | None = None) -> Metrics:
    return Metrics(namespace=NAMESPACE, service=service)