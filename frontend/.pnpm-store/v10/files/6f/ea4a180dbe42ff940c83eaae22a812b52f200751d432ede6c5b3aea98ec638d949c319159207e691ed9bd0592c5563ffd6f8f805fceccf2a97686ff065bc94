import { withIsolationScope, getCurrentScope, isObjectLike, extractTraceparentData, captureException, addNonEnumerableProperty } from '@sentry/core';

function storeCapturedEventIdOnError(error, eventId) {
  if (isObjectLike(error)) {
    addNonEnumerableProperty(error, "__sentry_event_id__", eventId);
  }
}
function isReactClassComponent(target) {
  return typeof target === "function" && target?.prototype?.isReactComponent;
}
function wrapPageComponentWithSentry(pageComponent) {
  if (isReactClassComponent(pageComponent)) {
    return class SentryWrappedPageComponent extends pageComponent {
      render(...args) {
        return withIsolationScope(() => {
          const scope = getCurrentScope();
          const sentryTraceData = isObjectLike(this.props) && "_sentryTraceData" in this.props && typeof this.props._sentryTraceData === "string" ? this.props._sentryTraceData : void 0;
          if (sentryTraceData) {
            const traceparentData = extractTraceparentData(sentryTraceData);
            scope.setContext("trace", {
              span_id: traceparentData?.parentSpanId,
              trace_id: traceparentData?.traceId
            });
          }
          try {
            return super.render(...args);
          } catch (e) {
            const eventId = captureException(e, {
              mechanism: {
                handled: false,
                type: "auto.function.nextjs.page_class"
              }
            });
            storeCapturedEventIdOnError(e, eventId);
            throw e;
          }
        });
      }
    };
  } else if (typeof pageComponent === "function") {
    return new Proxy(pageComponent, {
      apply(target, thisArg, argArray) {
        return withIsolationScope(() => {
          const scope = getCurrentScope();
          const sentryTraceData = argArray?.[0]?._sentryTraceData;
          if (sentryTraceData) {
            const traceparentData = extractTraceparentData(sentryTraceData);
            scope.setContext("trace", {
              span_id: traceparentData?.parentSpanId,
              trace_id: traceparentData?.traceId
            });
          }
          try {
            return target.apply(thisArg, argArray);
          } catch (e) {
            const eventId = captureException(e, {
              mechanism: {
                handled: false,
                type: "auto.function.nextjs.page_function"
              }
            });
            storeCapturedEventIdOnError(e, eventId);
            throw e;
          }
        });
      }
    });
  } else {
    return pageComponent;
  }
}

export { wrapPageComponentWithSentry };
//# sourceMappingURL=wrapPageComponentWithSentry.js.map
