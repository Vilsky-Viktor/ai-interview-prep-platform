
            {
              if (globalThis.performance === undefined) {
                globalThis.performance = {
                  timeOrigin: 0,
                  now: () => Date.now()
                };
              }
            }
          
Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const server = require('@sentry/core/server');
const noDiagnosticChannels = require('@sentry/server-utils/no-diagnostic-channels');
const api = require('@opentelemetry/api');
const node_async_hooks = require('node:async_hooks');

const gd="sentry.kind";

const SENTRY_TRACE_STATE_DSC = "sentry.dsc";
const SENTRY_TRACE_STATE_SAMPLED_NOT_RECORDING = "sentry.sampled_not_recording";
const SENTRY_SCOPES_CONTEXT_KEY = api.createContextKey("sentry_scopes");
const SENTRY_FORK_ISOLATION_SCOPE_CONTEXT_KEY = api.createContextKey("sentry_fork_isolation_scope");
const SENTRY_FORK_SET_SCOPE_CONTEXT_KEY = api.createContextKey("sentry_fork_set_scope");
const SENTRY_FORK_SET_ISOLATION_SCOPE_CONTEXT_KEY = api.createContextKey("sentry_fork_set_isolation_scope");
const SCOPE_CONTEXT_FIELD = "context";
function getScopesFromContext(context2) {
  return context2.getValue(SENTRY_SCOPES_CONTEXT_KEY);
}
function setScopesOnContext(context2, scopes) {
  return context2.setValue(SENTRY_SCOPES_CONTEXT_KEY, scopes);
}
function setContextOnScope(scope, context2) {
  scope.refs[SCOPE_CONTEXT_FIELD] = core.makeWeakRef(context2);
}
function getContextFromScope(scope) {
  return core.derefWeakRef(scope.refs[SCOPE_CONTEXT_FIELD]);
}
class TraceState {
  constructor() {
    this._internalState = /* @__PURE__ */ new Map();
  }
  /** @inheritDoc */
  set(key, value) {
    const next = this._clone();
    if (next._internalState.has(key)) {
      next._internalState.delete(key);
    }
    next._internalState.set(key, value);
    return next;
  }
  /** @inheritDoc */
  unset(key) {
    const next = this._clone();
    next._internalState.delete(key);
    return next;
  }
  /** @inheritDoc */
  get(key) {
    return this._internalState.get(key);
  }
  /** @inheritDoc */
  serialize() {
    return Array.from(this._internalState.keys()).reverse().map((key) => `${key}=${this._internalState.get(key)}`).join(",");
  }
  _clone() {
    const next = new TraceState();
    next._internalState = new Map(this._internalState);
    return next;
  }
}
function makeTraceState({
  dsc,
  sampled
}) {
  const dscString = dsc ? core.dynamicSamplingContextToSentryBaggageHeader(dsc) : void 0;
  const traceStateBase = new TraceState();
  const traceStateWithDsc = dscString ? traceStateBase.set(SENTRY_TRACE_STATE_DSC, dscString) : traceStateBase;
  return sampled === false ? traceStateWithDsc.set(SENTRY_TRACE_STATE_SAMPLED_NOT_RECORDING, "1") : traceStateWithDsc;
}
const SENTRY_TRACE_HEADER = "sentry-trace";
const SENTRY_BAGGAGE_HEADER = "baggage";
const W3C_TRACEPARENT_HEADER = "traceparent";
class SentryPropagator {
  /** @inheritDoc */
  inject(ctx, carrier, setter) {
    if (ctx !== api.context.active()) {
      core.consoleSandbox(() => {
        console.warn(
          "SentryPropagator: Injecting trace data of a different context than the active one is not supported. Skipping injection."
        );
      });
      return;
    }
    if (core.isTracingSuppressed()) {
      return;
    }
    const { propagateTraceparent } = core.getClient()?.getOptions() ?? {};
    const { "sentry-trace": sentryTrace, baggage, traceparent } = core.getTraceData({ propagateTraceparent });
    if (sentryTrace) {
      setter.set(carrier, SENTRY_TRACE_HEADER, sentryTrace);
    }
    if (baggage) {
      setter.set(carrier, SENTRY_BAGGAGE_HEADER, baggage);
    }
    if (traceparent) {
      setter.set(carrier, W3C_TRACEPARENT_HEADER, traceparent);
    }
  }
  /** @inheritDoc */
  extract(ctx, carrier, getter) {
    const maybeSentryTraceHeader = getter.get(carrier, SENTRY_TRACE_HEADER);
    const baggage = getter.get(carrier, SENTRY_BAGGAGE_HEADER);
    const sentryTrace = Array.isArray(maybeSentryTraceHeader) ? maybeSentryTraceHeader[0] : maybeSentryTraceHeader;
    return getContextWithRemoteActiveSpanAndScopes(ctx, { sentryTrace, baggage });
  }
  /** @inheritDoc */
  fields() {
    return [SENTRY_TRACE_HEADER, SENTRY_BAGGAGE_HEADER, W3C_TRACEPARENT_HEADER];
  }
}
function getContextWithRemoteActiveSpan(ctx, { sentryTrace, baggage }) {
  const propagationContext = core.propagationContextFromHeaders(sentryTrace, baggage);
  const { traceId, parentSpanId, sampled, dsc } = propagationContext;
  const client = core.getClient();
  const incomingDsc = core.baggageHeaderToDynamicSamplingContext(baggage);
  if (!parentSpanId || client && !core.shouldContinueTrace(client, incomingDsc?.org_id)) {
    return ctx;
  }
  const spanContext = generateRemoteSpanContext({
    traceId,
    spanId: parentSpanId,
    sampled,
    dsc
  });
  return api.trace.setSpanContext(ctx, spanContext);
}
function getContextWithRemoteActiveSpanAndScopes(ctx, options) {
  const ctxWithRemoteSpan = getContextWithRemoteActiveSpan(ctx, options);
  const isContinuingTrace2 = api.trace.getSpanContext(ctxWithRemoteSpan) !== void 0;
  return ensureScopesOnContext(ctxWithRemoteSpan, isContinuingTrace2);
}
function ensureScopesOnContext(ctx, isContinuingTrace2) {
  const scopes = getScopesFromContext(ctx);
  const scope = scopes ? scopes.scope : core.getCurrentScope().clone();
  if (!scopes && !isContinuingTrace2) {
    const propagationContext = scope.getPropagationContext();
    scope.setPropagationContext({
      ...propagationContext,
      traceId: core.generateTraceId(),
      sampleRand: core._INTERNAL_safeMathRandom()
    });
  }
  const newScopes = {
    scope,
    isolationScope: scopes ? scopes.isolationScope : core.getIsolationScope()
  };
  return setScopesOnContext(ctx, newScopes);
}
function generateRemoteSpanContext({
  spanId,
  traceId,
  sampled,
  dsc
}) {
  const traceState = makeTraceState({
    dsc,
    sampled
  });
  const spanContext = {
    traceId,
    spanId,
    isRemote: true,
    traceFlags: sampled ? api.TraceFlags.SAMPLED : api.TraceFlags.NONE,
    traceState
  };
  return spanContext;
}
const SUPPRESS_TRACING_KEY = api.createContextKey("OpenTelemetry SDK Context Key SUPPRESS_TRACING");
function isTracingSuppressed(context2) {
  return context2.getValue(SUPPRESS_TRACING_KEY) === true;
}
class SentryTracer {
  /** @inheritdoc */
  startSpan(name, options = {}, ctx) {
    const parentContext = ctx || api.context.active();
    const parentSpanCandidate = options.root ? void 0 : api.trace.getSpan(parentContext);
    const parentSpan = parentSpanCandidate && api.isSpanContextValid(parentSpanCandidate.spanContext()) ? parentSpanCandidate : void 0;
    if (isTracingSuppressed(parentContext)) {
      return this._createNonRecordingSpan(parentSpan);
    }
    const span = this._startSentrySpan(name, options, parentSpan, ctx !== void 0);
    core.markSpanAsTracerProviderSpan(span);
    return span;
  }
  startActiveSpan(name, optionsOrFn, contextOrFn, fn) {
    const options = typeof optionsOrFn === "function" ? {} : optionsOrFn;
    const explicitCtx = typeof contextOrFn === "function" || contextOrFn === void 0 ? void 0 : contextOrFn;
    const ctx = explicitCtx ?? api.context.active();
    const callback = typeof optionsOrFn === "function" ? optionsOrFn : typeof contextOrFn === "function" ? contextOrFn : fn;
    const span = this.startSpan(name, options, explicitCtx);
    const capturedIsolationScope = core.getCapturedScopesOnSpan(span).isolationScope;
    const withCapturedIsolationScope = (contextToFork) => capturedIsolationScope ? contextToFork.setValue(SENTRY_FORK_SET_ISOLATION_SCOPE_CONTEXT_KEY, capturedIsolationScope) : contextToFork;
    if (core.spanIsIgnored(span) && this._hasParentSpan(options, explicitCtx)) {
      return api.context.with(withCapturedIsolationScope(ctx), () => callback(span));
    }
    return api.context.with(withCapturedIsolationScope(api.trace.setSpan(ctx, span)), () => {
      if (api.trace.getSpan(api.context.active()) !== span) {
        return core.withScope((scope) => {
          core._INTERNAL_setSpanForScope(scope, span);
          return callback(span);
        });
      }
      core._INTERNAL_setSpanForScope(core.getCurrentScope(), span);
      return callback(span);
    });
  }
  /**
   * Whether a span started with these arguments gets a parent. Mirrors the parent lookup in `startSpan`
   * plus core's fallback to the scope's active span, which is what parents the span on runtimes without an
   * OTel context manager.
   */
  _hasParentSpan(options, explicitCtx) {
    if (options.root) {
      return false;
    }
    const parentSpan = explicitCtx ? api.trace.getSpan(explicitCtx) : core.getActiveSpan();
    return !!parentSpan && api.isSpanContextValid(parentSpan.spanContext());
  }
  _startSentrySpan(name, options, parentSpan, hasExplicitContext) {
    const sentryOptions = {
      name,
      attributes: options.attributes || {},
      links: options.links,
      startTime: options.startTime
    };
    if (options.kind) {
      sentryOptions.attributes[gd] = core.spanKindToName(options.kind);
    }
    if (options.root) {
      return core.startNewTrace(() => core.startInactiveSpan({ ...sentryOptions, parentSpan: null }));
    }
    if (parentSpan) {
      return core.startInactiveSpan({ ...sentryOptions, parentSpan });
    }
    return core.startInactiveSpan({
      ...sentryOptions,
      parentSpan: hasExplicitContext ? null : void 0
    });
  }
  _createNonRecordingSpan(parentSpan) {
    const traceId = parentSpan?.spanContext().traceId ?? core.getCurrentScope().getPropagationContext().traceId;
    const span = new core.SentryNonRecordingSpan({ traceId });
    if (parentSpan) {
      core.addChildSpanToSpan(parentSpan, span);
    }
    core.setCapturedScopesOnSpan(span, core.getCurrentScope(), core.getIsolationScope());
    return span;
  }
}
class SentryTracerProvider {
  constructor() {
    this._tracers = /* @__PURE__ */ new Map();
  }
  /** @inheritdoc */
  getTracer(name, version, options) {
    const key = JSON.stringify([name, version, options]);
    const cachedTracer = this._tracers.get(key);
    if (cachedTracer) {
      return cachedTracer;
    }
    const tracer = new SentryTracer();
    this._tracers.set(key, tracer);
    return tracer;
  }
  /** Compatibility with SDK tracer providers. */
  forceFlush() {
    return Promise.resolve();
  }
  /** Compatibility with SDK tracer providers. */
  shutdown() {
    return Promise.resolve();
  }
}
function withActiveSpan(span, callback) {
  const newContextWithActiveSpan = span ? api.trace.setSpan(api.context.active(), span) : api.trace.deleteSpan(api.context.active());
  return api.context.with(newContextWithActiveSpan, () => {
    const scope = core.getCurrentScope();
    core._INTERNAL_setSpanForScope(scope, span ?? void 0);
    return callback(scope);
  });
}
function getActiveSpan(scope) {
  const span = scope ? getSpanFromScope(scope) : api.trace.getActiveSpan();
  return span && api.isSpanContextValid(span.spanContext()) ? span : void 0;
}
function getSpanFromScope(scope) {
  const ctx = getContextFromScope(scope);
  return ctx ? api.trace.getSpan(ctx) : void 0;
}
function buildContextWithSentryScopes(context2) {
  const currentScopes = getScopesFromContext(context2);
  const currentScope = currentScopes?.scope || core.getCurrentScope();
  const currentIsolationScope = currentScopes?.isolationScope || core.getIsolationScope();
  const shouldForkIsolationScope = context2.getValue(SENTRY_FORK_ISOLATION_SCOPE_CONTEXT_KEY) === true;
  const scope = context2.getValue(SENTRY_FORK_SET_SCOPE_CONTEXT_KEY);
  const isolationScope = context2.getValue(SENTRY_FORK_SET_ISOLATION_SCOPE_CONTEXT_KEY);
  const newCurrentScope = scope || currentScope.clone();
  const newIsolationScope = isolationScope || (shouldForkIsolationScope ? currentIsolationScope.clone() : currentIsolationScope);
  const scopes = { scope: newCurrentScope, isolationScope: newIsolationScope };
  const ctx1 = setScopesOnContext(context2, scopes);
  const ctx2 = ctx1.deleteValue(SENTRY_FORK_ISOLATION_SCOPE_CONTEXT_KEY).deleteValue(SENTRY_FORK_SET_SCOPE_CONTEXT_KEY).deleteValue(SENTRY_FORK_SET_ISOLATION_SCOPE_CONTEXT_KEY);
  setContextOnScope(newCurrentScope, ctx2);
  return ctx2;
}
const ADD_LISTENER_METHODS = ["addListener", "on", "once", "prependListener", "prependOnceListener"];
class SentryAsyncLocalStorageContextManager {
  constructor(asyncLocalStorage) {
    this._kOtListeners = /* @__PURE__ */ Symbol("OtListeners");
    this._wrapped = false;
    this._asyncLocalStorage = asyncLocalStorage;
  }
  active() {
    return this._asyncLocalStorage.getStore() ?? api.ROOT_CONTEXT;
  }
  with(context2, fn, thisArg, ...args) {
    const ctx2 = buildContextWithSentryScopes(context2);
    const cb = thisArg == null ? fn : fn.bind(thisArg);
    return this._asyncLocalStorage.run(ctx2, cb, ...args);
  }
  enable() {
    return this;
  }
  disable() {
    try {
      this._asyncLocalStorage.disable();
    } catch {
    }
    return this;
  }
  bind(context2, target) {
    if (isEventEmitter(target)) {
      return this._bindEventEmitter(context2, target);
    }
    if (typeof target === "function") {
      return this._bindFunction(context2, target);
    }
    return target;
  }
  /**
   * Gets underlying AsyncLocalStorage and symbol to allow lookup of scope.
   * This is Sentry-specific.
   */
  getAsyncLocalStorageLookup() {
    return {
      asyncLocalStorage: this._asyncLocalStorage,
      contextSymbol: SENTRY_SCOPES_CONTEXT_KEY
    };
  }
  _bindFunction(context2, target) {
    const managerWith = this.with.bind(this);
    const contextWrapper = function(...args) {
      return managerWith(context2, () => target.apply(this, args));
    };
    Object.defineProperty(contextWrapper, "length", {
      enumerable: false,
      configurable: true,
      writable: false,
      value: target.length
    });
    return contextWrapper;
  }
  _bindEventEmitter(context2, ee) {
    if (this._getPatchMap(ee) !== void 0) {
      return ee;
    }
    if (this._createPatchMap(ee) === void 0) {
      return ee;
    }
    for (const methodName of ADD_LISTENER_METHODS) {
      const original = getMethod(ee, methodName);
      if (!original) continue;
      trySetMethod(ee, methodName, this._patchAddListener(ee, original, context2));
    }
    for (const methodName of ["removeListener", "off"]) {
      const original = getMethod(ee, methodName);
      if (!original) continue;
      trySetMethod(ee, methodName, this._patchRemoveListener(ee, original));
    }
    const removeAllListeners = getMethod(ee, "removeAllListeners");
    if (removeAllListeners) {
      trySetMethod(ee, "removeAllListeners", this._patchRemoveAllListeners(ee, removeAllListeners));
    }
    return ee;
  }
  _patchRemoveListener(ee, original) {
    const contextManager = this;
    return function(event, listener) {
      const events = contextManager._getPatchMap(ee)?.[event];
      if (events === void 0) {
        return original.call(this, event, listener);
      }
      const patchedListener = events.get(listener);
      return original.call(this, event, patchedListener || listener);
    };
  }
  _patchRemoveAllListeners(ee, original) {
    const contextManager = this;
    return function(event) {
      const map = contextManager._getPatchMap(ee);
      if (map !== void 0) {
        if (arguments.length === 0) {
          contextManager._createPatchMap(ee);
        } else if (event !== void 0 && map[event] !== void 0) {
          delete map[event];
        }
      }
      return original.apply(this, arguments);
    };
  }
  _patchAddListener(ee, original, context2) {
    const contextManager = this;
    return function(event, listener) {
      if (contextManager._wrapped) {
        return original.call(this, event, listener);
      }
      const map = contextManager._getPatchMap(ee) ?? contextManager._createPatchMap(ee);
      if (map === void 0) {
        return original.call(this, event, listener);
      }
      let listeners = map[event];
      if (listeners === void 0) {
        listeners = /* @__PURE__ */ new WeakMap();
        map[event] = listeners;
      }
      const patchedListener = contextManager.bind(context2, listener);
      listeners.set(listener, patchedListener);
      contextManager._wrapped = true;
      try {
        return original.call(this, event, patchedListener);
      } finally {
        contextManager._wrapped = false;
      }
    };
  }
  /**
   * Attach a fresh patch map to the emitter. Returns `undefined` if the emitter does not accept the
   * property (e.g. it is frozen or sealed), in which case the emitter must not be patched at all —
   * without a patch map the remove-listener patches could not resolve their wrapped listeners.
   */
  _createPatchMap(ee) {
    const map = /* @__PURE__ */ Object.create(null);
    try {
      ee[this._kOtListeners] = map;
    } catch {
      return void 0;
    }
    return this._getPatchMap(ee) === map ? map : void 0;
  }
  _getPatchMap(ee) {
    return ee[this._kOtListeners];
  }
}
function isEventEmitter(target) {
  if (typeof target !== "object" || !target) {
    return false;
  }
  const candidate = target;
  return typeof candidate.on === "function" && typeof candidate.emit === "function";
}
function getMethod(ee, methodName) {
  const value = ee[methodName];
  return typeof value === "function" ? value : void 0;
}
function trySetMethod(ee, methodName, patched) {
  try {
    ee[methodName] = patched;
  } catch {
  }
}
function setOpenTelemetryContextAsyncContextStrategy() {
  const existingAsyncLocalStorage = core.getAsyncContextStrategy(core.getMainCarrier()).getTracingChannelBinding?.()?.asyncLocalStorage;
  const asyncLocalStorage = existingAsyncLocalStorage ?? new node_async_hooks.AsyncLocalStorage();
  function getScopes() {
    const ctx = api.context.active();
    const scopes = getScopesFromContext(ctx);
    if (scopes) {
      return scopes;
    }
    return {
      scope: core.getDefaultCurrentScope(),
      isolationScope: core.getDefaultIsolationScope()
    };
  }
  function withScope2(callback) {
    const ctx = api.context.active();
    return api.context.with(ctx, () => {
      return callback(getCurrentScope2());
    });
  }
  function withSetScope(scope, callback) {
    const ctx = getContextFromScope(scope) || api.context.active();
    return api.context.with(ctx.setValue(SENTRY_FORK_SET_SCOPE_CONTEXT_KEY, scope), () => {
      return callback(scope);
    });
  }
  function withIsolationScope(callback) {
    const ctx = api.context.active();
    return api.context.with(ctx.setValue(SENTRY_FORK_ISOLATION_SCOPE_CONTEXT_KEY, true), () => {
      const scope = getCurrentScope2();
      if (!core.isContinuingTrace(scope.getPropagationContext())) {
        scope.setPropagationContext({
          traceId: core.generateTraceId(),
          sampleRand: core._INTERNAL_safeMathRandom()
        });
      }
      return callback(getIsolationScope2());
    });
  }
  function withSetIsolationScope(isolationScope, callback) {
    const ctx = api.context.active();
    return api.context.with(ctx.setValue(SENTRY_FORK_SET_ISOLATION_SCOPE_CONTEXT_KEY, isolationScope), () => {
      return callback(getIsolationScope2());
    });
  }
  function getCurrentScope2() {
    return getScopes().scope;
  }
  function getIsolationScope2() {
    return getScopes().isolationScope;
  }
  function getTracingChannelBinding() {
    return {
      asyncLocalStorage
    };
  }
  core.setAsyncContextStrategy({
    withScope: withScope2,
    withSetScope,
    withSetIsolationScope,
    withIsolationScope,
    getCurrentScope: getCurrentScope2,
    getIsolationScope: getIsolationScope2,
    getActiveSpan,
    // The types here don't fully align, because our own `Span` type is narrower
    // than the OTEL one - but this is OK for here, as we now we'll only have OTEL spans passed around
    withActiveSpan,
    getTracingChannelBinding
  });
  const ctxManager = new SentryAsyncLocalStorageContextManager(asyncLocalStorage);
  api.context.setGlobalContextManager(ctxManager);
  return ctxManager.getAsyncLocalStorageLookup();
}
function getSamplingDecision(spanContext) {
  const { traceFlags, traceState } = spanContext;
  const sampledNotRecording = traceState ? traceState.get(SENTRY_TRACE_STATE_SAMPLED_NOT_RECORDING) === "1" : false;
  if (traceFlags === api.TraceFlags.SAMPLED) {
    return true;
  }
  if (sampledNotRecording) {
    return false;
  }
  const dscString = traceState ? traceState.get(SENTRY_TRACE_STATE_DSC) : void 0;
  const dsc = dscString ? core.baggageHeaderToDynamicSamplingContext(dscString) : void 0;
  if (dsc?.sampled === "true") {
    return true;
  }
  if (dsc?.sampled === "false") {
    return false;
  }
  return void 0;
}
function registerPrepareSpanScope(client) {
  client.on("prepareSpanScope", (spanScope) => {
    const { scope, parentSpan } = spanScope;
    if (!parentSpan?.spanContext().isRemote) {
      return;
    }
    const { spanId, traceId, traceState } = parentSpan.spanContext();
    const dsc = core.getDynamicSamplingContextFromSpan(parentSpan);
    const sampleRand = typeof dsc.sample_rand === "string" ? Number(dsc.sample_rand) : void 0;
    const hasIncomingDsc = !!traceState?.get(SENTRY_TRACE_STATE_DSC);
    const forkedScope = scope.clone();
    forkedScope.setPropagationContext({
      traceId,
      parentSpanId: spanId,
      sampled: getSamplingDecision(parentSpan.spanContext()),
      dsc: hasIncomingDsc ? dsc : void 0,
      sampleRand: typeof sampleRand === "number" && !Number.isNaN(sampleRand) ? sampleRand : core._INTERNAL_safeMathRandom()
    });
    core._INTERNAL_setSpanForScope(forkedScope, void 0);
    spanScope.scope = forkedScope;
    spanScope.parentSpan = void 0;
  });
}

class VercelEdgeClient extends server.ServerRuntimeClient {
  /**
   * Creates a new Vercel Edge Runtime SDK instance.
   * @param options Configuration options for this SDK.
   */
  constructor(options) {
    core.applySdkMetadata(options, "vercel-edge");
    options._metadata = options._metadata || {};
    const clientOptions = {
      ...options,
      platform: "javascript",
      // Use provided runtime or default to 'vercel-edge'
      runtime: options.runtime || { name: "vercel-edge" },
      serverName: options.serverName || process.env.SENTRY_NAME,
      _flushInterval: 0
    };
    super(clientOptions);
    registerPrepareSpanScope(this);
  }
  // Eslint ignore explanation: This is already documented in super.
  // eslint-disable-next-line jsdoc/require-jsdoc
  async flush(timeout) {
    const provider = this.traceProvider;
    await provider?.forceFlush();
    if (this.getOptions().sendClientReports) {
      this._flushOutcomes();
    }
    return super.flush(timeout);
  }
}

const winterCGFetchIntegration = core.createFetchIntegration({
  name: "WinterCGFetch",
  spanOrigin: "auto.http.wintercg_fetch"
});

const DEFAULT_TRANSPORT_BUFFER_SIZE = 30;
class IsolatedPromiseBuffer {
  constructor(_bufferSize = DEFAULT_TRANSPORT_BUFFER_SIZE) {
    this.$ = [];
    this._taskProducers = [];
    this._bufferSize = _bufferSize;
  }
  /**
   * @inheritdoc
   */
  add(taskProducer) {
    if (this._taskProducers.length >= this._bufferSize) {
      return Promise.reject(core.SENTRY_BUFFER_FULL_ERROR);
    }
    this._taskProducers.push(taskProducer);
    return Promise.resolve({});
  }
  /**
   * @inheritdoc
   */
  drain(timeout) {
    const oldTaskProducers = [...this._taskProducers];
    this._taskProducers = [];
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        if (timeout && timeout > 0) {
          resolve(false);
        }
      }, timeout);
      Promise.all(
        oldTaskProducers.map(
          (taskProducer) => taskProducer().then(null, () => {
          })
        )
      ).then(() => {
        clearTimeout(timer);
        resolve(true);
      });
    });
  }
}
function makeEdgeTransport(options) {
  function makeRequest(request) {
    const requestOptions = {
      body: request.body,
      method: "POST",
      headers: options.headers,
      ...options.fetchOptions
    };
    return core.suppressTracing(() => {
      return fetch(options.url, requestOptions).then((response) => {
        return {
          statusCode: response.status,
          headers: {
            "x-sentry-rate-limits": response.headers.get("X-Sentry-Rate-Limits"),
            "retry-after": response.headers.get("Retry-After")
          }
        };
      });
    });
  }
  return core.createTransport(options, makeRequest, new IsolatedPromiseBuffer(options.bufferSize));
}

const nodeStackParser = core.createStackParser(server.nodeStackLineParser());
function getDefaultIntegrations() {
  return [
    core.dedupeIntegration(),
    core.eventFiltersIntegration(),
    core.functionToStringIntegration(),
    core.conversationIdIntegration(),
    core.linkedErrorsIntegration(),
    winterCGFetchIntegration(),
    core.consoleIntegration(),
    core.requestDataIntegration()
  ];
}
function init(options = {}) {
  setOpenTelemetryContextAsyncContextStrategy();
  const scope = core.getCurrentScope();
  scope.update(options.initialScope);
  if (options.defaultIntegrations === void 0) {
    options.defaultIntegrations = getDefaultIntegrations();
  }
  if (options.dsn === void 0 && process.env.SENTRY_DSN) {
    options.dsn = process.env.SENTRY_DSN;
  }
  if (options.tracesSampleRate === void 0 && process.env.SENTRY_TRACES_SAMPLE_RATE) {
    const tracesSampleRate = parseFloat(process.env.SENTRY_TRACES_SAMPLE_RATE);
    if (isFinite(tracesSampleRate)) {
      options.tracesSampleRate = tracesSampleRate;
    }
  }
  if (options.release === void 0) {
    const detectedRelease = getSentryRelease();
    if (detectedRelease !== void 0) {
      options.release = detectedRelease;
    }
  }
  options.environment = options.environment || process.env.SENTRY_ENVIRONMENT || core.getVercelEnv() || process.env.NODE_ENV;
  options.traceLifecycle = options.traceLifecycle ?? getTraceLifecycleFromEnv(process.env.SENTRY_TRACE_LIFECYCLE);
  const client = new VercelEdgeClient({
    ...options,
    stackParser: core.stackParserFromStackParserOptions(options.stackParser || nodeStackParser),
    integrations: core.getIntegrationsToSetup(options),
    transport: options.transport || makeEdgeTransport
  });
  core.getCurrentScope().setClient(client);
  client.init();
  if (options.enableOpenTelemetrySetup ?? true) {
    setupOtel(client);
  }
  return client;
}
function setupOtel(client) {
  if (client.getOptions().debug) {
    setupOpenTelemetryLogger();
  }
  const provider = new SentryTracerProvider();
  api.trace.setGlobalTracerProvider(provider);
  api.propagation.setGlobalPropagator(new SentryPropagator());
  client.traceProvider = provider;
}
function setupOpenTelemetryLogger() {
  api.diag.disable();
  api.diag.setLogger(
    {
      error: core.debug.error,
      warn: core.debug.warn,
      info: core.debug.log,
      debug: core.debug.log,
      verbose: core.debug.log
    },
    api.DiagLogLevel.DEBUG
  );
}
function getSentryRelease(fallback) {
  if (process.env.SENTRY_RELEASE) {
    return process.env.SENTRY_RELEASE;
  }
  if (core.GLOBAL_OBJ.SENTRY_RELEASE?.id) {
    return core.GLOBAL_OBJ.SENTRY_RELEASE.id;
  }
  const possibleReleaseNameOfGitProvider = (
    // GitHub Actions - https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
    process.env["GITHUB_SHA"] || // GitLab CI - https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    process.env["CI_MERGE_REQUEST_SOURCE_BRANCH_SHA"] || process.env["CI_BUILD_REF"] || process.env["CI_COMMIT_SHA"] || // Bitbucket - https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
    process.env["BITBUCKET_COMMIT"]
  );
  const possibleReleaseNameOfCiProvidersWithSpecificEnvVar = (
    // AppVeyor - https://www.appveyor.com/docs/environment-variables/
    process.env["APPVEYOR_PULL_REQUEST_HEAD_COMMIT"] || process.env["APPVEYOR_REPO_COMMIT"] || // AWS CodeBuild - https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
    process.env["CODEBUILD_RESOLVED_SOURCE_VERSION"] || // AWS Amplify - https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html
    process.env["AWS_COMMIT_ID"] || // Azure Pipelines - https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml
    process.env["BUILD_SOURCEVERSION"] || // Bitrise - https://devcenter.bitrise.io/builds/available-environment-variables/
    process.env["GIT_CLONE_COMMIT_HASH"] || // Buddy CI - https://buddy.works/docs/pipelines/environment-variables#default-environment-variables
    process.env["BUDDY_EXECUTION_REVISION"] || // Builtkite - https://buildkite.com/docs/pipelines/environment-variables
    process.env["BUILDKITE_COMMIT"] || // CircleCI - https://circleci.com/docs/variables/
    process.env["CIRCLE_SHA1"] || // Cirrus CI - https://cirrus-ci.org/guide/writing-tasks/#environment-variables
    process.env["CIRRUS_CHANGE_IN_REPO"] || // Codefresh - https://codefresh.io/docs/docs/codefresh-yaml/variables/
    process.env["CF_REVISION"] || // Codemagic - https://docs.codemagic.io/yaml-basic-configuration/environment-variables/
    process.env["CM_COMMIT"] || // Cloudflare Pages - https://developers.cloudflare.com/pages/platform/build-configuration/#environment-variables
    process.env["CF_PAGES_COMMIT_SHA"] || // Drone - https://docs.drone.io/pipeline/environment/reference/
    process.env["DRONE_COMMIT_SHA"] || // Flightcontrol - https://www.flightcontrol.dev/docs/guides/flightcontrol/environment-variables#built-in-environment-variables
    process.env["FC_GIT_COMMIT_SHA"] || // Heroku #1 https://devcenter.heroku.com/articles/heroku-ci
    process.env["HEROKU_TEST_RUN_COMMIT_VERSION"] || // Heroku #2 https://devcenter.heroku.com/articles/dyno-metadata#dyno-metadata
    process.env["HEROKU_BUILD_COMMIT"] || // Heroku #3 (deprecated by Heroku, kept for backward compatibility)
    process.env["HEROKU_SLUG_COMMIT"] || // Railway - https://docs.railway.app/reference/variables#git-variables
    process.env["RAILWAY_GIT_COMMIT_SHA"] || // Render - https://render.com/docs/environment-variables
    process.env["RENDER_GIT_COMMIT"] || // Semaphore CI - https://docs.semaphoreci.com/ci-cd-environment/environment-variables
    process.env["SEMAPHORE_GIT_SHA"] || // TravisCI - https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
    process.env["TRAVIS_PULL_REQUEST_SHA"] || // Vercel - https://vercel.com/docs/v2/build-step#system-environment-variables
    process.env["VERCEL_GIT_COMMIT_SHA"] || process.env["VERCEL_GITHUB_COMMIT_SHA"] || process.env["VERCEL_GITLAB_COMMIT_SHA"] || process.env["VERCEL_BITBUCKET_COMMIT_SHA"] || // Zeit (now known as Vercel)
    process.env["ZEIT_GITHUB_COMMIT_SHA"] || process.env["ZEIT_GITLAB_COMMIT_SHA"] || process.env["ZEIT_BITBUCKET_COMMIT_SHA"]
  );
  const possibleReleaseNameOfCiProvidersWithGenericEnvVar = (
    // CloudBees CodeShip - https://docs.cloudbees.com/docs/cloudbees-codeship/latest/pro-builds-and-configuration/environment-variables
    process.env["CI_COMMIT_ID"] || // Coolify - https://coolify.io/docs/knowledge-base/environment-variables
    process.env["SOURCE_COMMIT"] || // Heroku #3 https://devcenter.heroku.com/changelog-items/630
    process.env["SOURCE_VERSION"] || // Jenkins - https://plugins.jenkins.io/git/#environment-variables
    process.env["GIT_COMMIT"] || // Netlify - https://docs.netlify.com/configure-builds/environment-variables/#build-metadata
    process.env["COMMIT_REF"] || // TeamCity - https://www.jetbrains.com/help/teamcity/predefined-build-parameters.html
    process.env["BUILD_VCS_NUMBER"] || // Woodpecker CI - https://woodpecker-ci.org/docs/usage/environment
    process.env["CI_COMMIT_SHA"]
  );
  return possibleReleaseNameOfGitProvider || possibleReleaseNameOfCiProvidersWithSpecificEnvVar || possibleReleaseNameOfCiProvidersWithGenericEnvVar || fallback;
}
function getTraceLifecycleFromEnv(envVar) {
  return envVar === "stream" || envVar === "static" ? envVar : void 0;
}

exports.SDK_VERSION = core.SDK_VERSION;
exports.SEMANTIC_ATTRIBUTE_SENTRY_OP = core.SEMANTIC_ATTRIBUTE_SENTRY_OP;
exports.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN = core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN;
exports.SEMANTIC_ATTRIBUTE_SENTRY_SAMPLE_RATE = core.SEMANTIC_ATTRIBUTE_SENTRY_SAMPLE_RATE;
exports.Scope = core.Scope;
exports.addBreadcrumb = core.addBreadcrumb;
exports.addEventProcessor = core.addEventProcessor;
exports.addIntegration = core.addIntegration;
exports.bindScopeToEmitter = core.bindScopeToEmitter;
exports.captureCheckIn = core.captureCheckIn;
exports.captureConsoleIntegration = core.captureConsoleIntegration;
exports.captureEvent = core.captureEvent;
exports.captureException = core.captureException;
exports.captureFeedback = core.captureFeedback;
exports.captureMessage = core.captureMessage;
exports.close = core.close;
exports.consoleIntegration = core.consoleIntegration;
exports.consoleLoggingIntegration = core.consoleLoggingIntegration;
exports.continueTrace = core.continueTrace;
exports.createConsolaReporter = core.createConsolaReporter;
exports.createTransport = core.createTransport;
exports.dedupeIntegration = core.dedupeIntegration;
exports.eventFiltersIntegration = core.eventFiltersIntegration;
exports.extraErrorDataIntegration = core.extraErrorDataIntegration;
exports.featureFlagsIntegration = core.featureFlagsIntegration;
exports.flush = core.flush;
exports.functionToStringIntegration = core.functionToStringIntegration;
exports.getActiveSpan = core.getActiveSpan;
exports.getClient = core.getClient;
exports.getCurrentScope = core.getCurrentScope;
exports.getGlobalScope = core.getGlobalScope;
exports.getIsolationScope = core.getIsolationScope;
exports.getRootSpan = core.getRootSpan;
exports.getSpanDescendants = core.getSpanDescendants;
exports.getSpanStatusFromHttpCode = core.getSpanStatusFromHttpCode;
exports.getTraceData = core.getTraceData;
exports.getTraceMetaTags = core.getTraceMetaTags;
exports.instrumentSupabaseClient = core.instrumentSupabaseClient;
exports.isEnabled = core.isEnabled;
exports.isInitialized = core.isInitialized;
exports.lastEventId = core.lastEventId;
exports.linkedErrorsIntegration = core.linkedErrorsIntegration;
exports.logger = core.logger;
exports.metrics = core.metrics;
exports.moduleMetadataIntegration = core.moduleMetadataIntegration;
exports.requestDataIntegration = core.requestDataIntegration;
exports.rewriteFramesIntegration = core.rewriteFramesIntegration;
exports.setAttribute = core.setAttribute;
exports.setAttributes = core.setAttributes;
exports.setContext = core.setContext;
exports.setCurrentClient = core.setCurrentClient;
exports.setExtra = core.setExtra;
exports.setExtras = core.setExtras;
exports.setHttpStatus = core.setHttpStatus;
exports.setMeasurement = core.setMeasurement;
exports.setTag = core.setTag;
exports.setTags = core.setTags;
exports.setUser = core.setUser;
exports.spanStreamingIntegration = core.spanStreamingIntegration;
exports.spanToBaggageHeader = core.spanToBaggageHeader;
exports.spanToJSON = core.spanToJSON;
exports.spanToStaticSpanJSON = core.spanToStaticSpanJSON;
exports.spanToTraceHeader = core.spanToTraceHeader;
exports.startInactiveSpan = core.startInactiveSpan;
exports.startNewTrace = core.startNewTrace;
exports.startSpan = core.startSpan;
exports.startSpanManual = core.startSpanManual;
exports.supabaseIntegration = core.supabaseIntegration;
exports.suppressTracing = core.suppressTracing;
exports.withActiveSpan = core.withActiveSpan;
exports.withIsolationScope = core.withIsolationScope;
exports.withMonitor = core.withMonitor;
exports.withScope = core.withScope;
exports.withStaticSpan = core.withStaticSpan;
exports.withStreamedSpan = core.withStreamedSpan;
exports.zodErrorsIntegration = core.zodErrorsIntegration;
exports.trpcMiddleware = server.trpcMiddleware;
exports.wrapMcpServerWithSentry = server.wrapMcpServerWithSentry;
exports.createLangChainCallbackHandler = noDiagnosticChannels.createLangChainCallbackHandler;
exports.getOtlpTracesEndpoint = noDiagnosticChannels.getOtlpTracesEndpoint;
exports.instrumentAnthropicAiClient = noDiagnosticChannels.instrumentAnthropicAiClient;
exports.instrumentGoogleGenAIClient = noDiagnosticChannels.instrumentGoogleGenAIClient;
exports.instrumentLangChainEmbeddings = noDiagnosticChannels.instrumentLangChainEmbeddings;
exports.instrumentMistralAiClient = noDiagnosticChannels.instrumentMistralAiClient;
exports.instrumentOpenAiClient = noDiagnosticChannels.instrumentOpenAiClient;
exports.instrumentStateGraph = noDiagnosticChannels.instrumentStateGraph;
exports.instrumentTypeSafeClient = noDiagnosticChannels.instrumentTypeSafeClient;
exports.openTelemetryIntegration = noDiagnosticChannels.openTelemetryIntegration;
exports.VercelEdgeClient = VercelEdgeClient;
exports.getDefaultIntegrations = getDefaultIntegrations;
exports.init = init;
exports.winterCGFetchIntegration = winterCGFetchIntegration;
//# sourceMappingURL=index.js.map
