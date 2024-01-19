import sentry_sdk
from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.trace import TracerProvider
from sentry_sdk.integrations.opentelemetry import SentrySpanProcessor, SentryPropagator
import environment as env
from environment import logging


def sentry_configuration():
    if env.sentry_dsn:
        
        logging.info("🔧  Sentry configured")
        sentry_sdk.init(
            dsn=env.sentry_dsn,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
                instrumenter="otel",

        )
        provider = TracerProvider()
        provider.add_span_processor(SentrySpanProcessor())
        trace.set_tracer_provider(provider)
        set_global_textmap(SentryPropagator())
    
