import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { Resource } from '@opentelemetry/resources';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { trace, type Tracer } from '@opentelemetry/api';

let tracer: Tracer | null = null;

export function initTelemetry() {
  const otlpEndpoint =
    import.meta.env.VITE_OTEL_ENDPOINT || 'http://localhost:4318';

  const resource = new Resource({
    'service.name': 'vacanceai-frontend',
    'service.version': '1.0.0',
  });

  const exporter = new OTLPTraceExporter({
    url: `${otlpEndpoint}/v1/traces`,
  });

  const provider = new WebTracerProvider({
    resource,
    spanProcessors: [new BatchSpanProcessor(exporter)],
  });

  provider.register({
    contextManager: new ZoneContextManager(),
  });

  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: [/.*/],
      }),
      new XMLHttpRequestInstrumentation({
        propagateTraceHeaderCorsUrls: [/.*/],
      }),
    ],
  });

  tracer = trace.getTracer('vacanceai-frontend');

  console.log(`OpenTelemetry initialized — exporting to ${otlpEndpoint}`);
}

/**
 * Create a simple span for chat events.
 * Safe to call even if telemetry is not initialized.
 */
export function traceChat(
  name: string,
  attributes?: Record<string, string | number | boolean>,
) {
  if (!tracer) return;

  const span = tracer.startSpan(name);
  if (attributes) {
    for (const [key, value] of Object.entries(attributes)) {
      span.setAttribute(key, value);
    }
  }
  span.end();
}
