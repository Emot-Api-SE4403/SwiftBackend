from fastapi import FastAPI
from grpc import ChannelCredentials
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.boto3sqs import Boto3SQSInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus_remote_write import (
    PrometheusRemoteWriteMetricsExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry import trace, metrics
from dotenv import load_dotenv
import os

otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"), insecure=True)
pr_exporter = PrometheusRemoteWriteMetricsExporter(
    os.getenv("PR_EXPORTER_OTLP_ENDPOINT"),
    basic_auth= {
        "username": os.getenv("PR_USERNAME"),
        "password": os.getenv("PR_PASSWORD")
    }
)

resource = Resource(attributes={
    "service.name": os.getenv('OTEL_SERVICE_NAME')
})

reader = PeriodicExportingMetricReader(pr_exporter, 1000)
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)


trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

def load_main_analytics(app: FastAPI) :
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace,
        meter_provider=metrics
    )

def load_database_analytics(engine):
    Boto3SQSInstrumentor().instrument(
        tracer_provider=trace,
        meter_provider=metrics
    )
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        tracer_provider=trace,
        meter_provider=metrics
    )
