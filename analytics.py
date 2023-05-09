from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.boto3sqs import Boto3SQSInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from dotenv import load_dotenv
import os

resource = Resource(attributes={
    "service.name": os.getenv('OTEL_SERVICE_NAME')
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"), insecure=True)

span_processor = BatchSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

def load_main_analytics(app: FastAPI) :
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace
    )

def load_database_analytics(engine):
    Boto3SQSInstrumentor().instrument(
        tracer_provider=trace
    )
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        tracer_provider=trace
    )
