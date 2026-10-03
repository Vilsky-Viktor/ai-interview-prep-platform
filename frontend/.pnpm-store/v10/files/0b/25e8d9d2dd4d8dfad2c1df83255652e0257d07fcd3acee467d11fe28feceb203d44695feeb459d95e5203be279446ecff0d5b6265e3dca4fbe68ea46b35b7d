Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');
const React = require('react');
const debugBuild = require('../debug-build.js');
const hoistNonReactStatics = require('../hoist-non-react-statics.js');
const lazyRoutes = require('./lazy-routes.js');
const utils = require('./utils.js');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');

const reactRouterConfigByClient = /* @__PURE__ */ new WeakMap();
function getRouterConfig(client) {
  return client ? reactRouterConfigByClient.get(client) : void 0;
}
const useIsomorphicLayoutEffect = browser.WINDOW?.document ? React.useLayoutEffect : React.useEffect;
const activeNavigationSpans = /* @__PURE__ */ new WeakMap();
const allRoutes = /* @__PURE__ */ new Set();
const pendingLazyRouteLoads = /* @__PURE__ */ new WeakMap();
const deferredLazyRouteResolvers = /* @__PURE__ */ new WeakMap();
function scheduleCallback(callback) {
  if (browser.WINDOW?.requestAnimationFrame) {
    return browser.WINDOW.requestAnimationFrame(callback);
  }
  return setTimeout(callback, 0);
}
function cancelScheduledCallback(id) {
  if (browser.WINDOW?.cancelAnimationFrame) {
    browser.WINDOW.cancelAnimationFrame(id);
  } else {
    clearTimeout(id);
  }
}
function computeLocationKey(location) {
  return `${location.pathname}${location.search || ""}${location.hash || ""}`;
}
function isParameterizedRoute(routeName) {
  return routeName.includes(":") || routeName.includes("*");
}
function shouldSkipNavigation(trackedNav, locationKey, proposedName, spanHasEnded) {
  if (!trackedNav) {
    return { skip: false, shouldUpdate: false };
  }
  const isDuplicate = trackedNav.locationKey === locationKey && (trackedNav.isPlaceholder || !spanHasEnded);
  if (isDuplicate) {
    const currentHasWildcard = !!trackedNav.routeName && utils.transactionNameHasWildcard(trackedNav.routeName);
    const proposedHasWildcard = utils.transactionNameHasWildcard(proposedName);
    const currentIsParameterized = !!trackedNav.routeName && isParameterizedRoute(trackedNav.routeName);
    const proposedIsParameterized = isParameterizedRoute(proposedName);
    const isWildcardUpgrade = currentHasWildcard && !proposedHasWildcard;
    const isRawToParameterized = !currentIsParameterized && proposedIsParameterized;
    const isMoreSpecific = proposedName !== trackedNav.routeName && proposedName.length > (trackedNav.routeName?.length || 0) && !proposedHasWildcard;
    const shouldUpdate = !!(trackedNav.routeName && (isWildcardUpgrade || isRawToParameterized || isMoreSpecific));
    return { skip: true, shouldUpdate };
  }
  return { skip: false, shouldUpdate: false };
}
function addResolvedRoutesToParent(resolvedRoutes, parentRoute) {
  const existingChildren = parentRoute.children || [];
  const newRoutes = resolvedRoutes.filter(
    (newRoute) => !existingChildren.some(
      (existing) => existing === newRoute || newRoute.path && existing.path === newRoute.path || newRoute.id && existing.id === newRoute.id
    )
  );
  if (newRoutes.length > 0) {
    parentRoute.children = [...existingChildren, ...newRoutes];
  }
}
function trackLazyRouteLoad(span, promise) {
  let promises = pendingLazyRouteLoads.get(span);
  if (!promises) {
    promises = /* @__PURE__ */ new Set();
    pendingLazyRouteLoads.set(span, promises);
  }
  promises.add(promise);
  promise.finally(() => {
    const currentPromises = pendingLazyRouteLoads.get(span);
    if (currentPromises) {
      currentPromises.delete(promise);
    }
  });
}
function createDeferredLazyRoutePromise(span) {
  const deferredPromise = new Promise((resolve) => {
    deferredLazyRouteResolvers.set(span, resolve);
  });
  trackLazyRouteLoad(span, deferredPromise);
}
function resolveDeferredLazyRoutePromise(span) {
  const resolver = deferredLazyRouteResolvers.get(span);
  if (resolver) {
    resolver();
    deferredLazyRouteResolvers.delete(span);
    if (span.__sentry_may_have_lazy_routes__) {
      span.__sentry_may_have_lazy_routes__ = false;
    }
  }
}
function processResolvedRoutes(resolvedRoutes, config, parentRoute, currentLocation = null, capturedSpan) {
  resolvedRoutes.forEach((child) => {
    allRoutes.add(child);
    if (config.enableAsyncRouteHandlers) {
      lazyRoutes.checkRouteForAsyncHandler(child, (r, p, l, s) => processResolvedRoutes(r, config, p, l, s));
    }
  });
  if (parentRoute) {
    addResolvedRoutesToParent(resolvedRoutes, parentRoute);
  }
  const targetSpan = capturedSpan ?? utils.getActiveRootSpan();
  if (targetSpan) {
    const { end_timestamp, attributes: attributes$1 } = core.spanToJSON(targetSpan);
    if (end_timestamp) {
      debugBuild.DEBUG_BUILD && core.debug.warn("[React Router] Lazy handler resolved after span ended - skipping update");
      return;
    }
    const spanOp = attributes$1[attributes.SENTRY_OP];
    let location = currentLocation;
    if (!location && !capturedSpan) {
      if (typeof browser.WINDOW !== "undefined") {
        const globalLocation = browser.WINDOW.location;
        if (globalLocation?.pathname) {
          location = { pathname: globalLocation.pathname };
        }
      }
    }
    if (location) {
      if (spanOp === "pageload") {
        updatePageloadTransaction({
          activeRootSpan: targetSpan,
          location: { pathname: location.pathname },
          routes: Array.from(allRoutes),
          allRoutes: Array.from(allRoutes),
          config
        });
      } else if (spanOp === "navigation") {
        updateNavigationSpan(targetSpan, location, Array.from(allRoutes), false, config);
      }
    }
  }
}
function updateNavigationSpan(activeRootSpan, location, allRoutes2, forceUpdate = false, config) {
  const { name: currentName, end_timestamp, attributes: attributes$1 } = core.spanToJSON(activeRootSpan);
  const spanPathname = activeRootSpan?.__sentry_navigation_pathname__;
  if (spanPathname !== void 0 && spanPathname !== location.pathname) {
    debugBuild.DEBUG_BUILD && core.debug.log(
      `[React Router] Not renaming the navigation span for "${spanPathname}" with the route of "${location.pathname}"`
    );
    return;
  }
  const hasBeenNamed = activeRootSpan?.__sentry_navigation_name_set__;
  const currentNameHasWildcard = currentName && utils.transactionNameHasWildcard(currentName);
  const shouldUpdate = !hasBeenNamed || forceUpdate || currentNameHasWildcard;
  if (shouldUpdate && !end_timestamp) {
    const currentBranches = config.matchRoutes(allRoutes2, location);
    const [name, source] = utils.resolveRouteNameAndSource(
      location,
      allRoutes2,
      allRoutes2,
      currentBranches || [],
      config
    );
    const currentSource = attributes$1[attributes.SENTRY_SEGMENT_NAME_SOURCE];
    const isImprovement = name && (!currentName || // No current name - always set
    !hasBeenNamed && (currentSource !== "route" || source === "route") || // Not finalized - allow unless downgrading route→url
    currentSource !== "route" && source === "route" || // URL → route upgrade
    currentSource === "route" && source === "route" && currentNameHasWildcard);
    if (isImprovement) {
      const client = core.getClient();
      const isUnparameterizedStreamedNavigation = source !== "route" && !!client && core.hasSpanStreamingEnabled(client);
      activeRootSpan.updateName(isUnparameterizedStreamedNavigation ? core.NAVIGATION_SPAN_NAME_FALLBACK : name);
      activeRootSpan.setAttribute(attributes.SENTRY_SEGMENT_NAME_SOURCE, source);
      if (source === "route") {
        activeRootSpan.setAttribute(attributes.URL_TEMPLATE, name);
      }
      if (!utils.transactionNameHasWildcard(name) && source === "route") {
        core.addNonEnumerableProperty(activeRootSpan, "__sentry_navigation_name_set__", true);
      }
    }
  }
}
function setupRouterSubscription(router, routes, version, activeRootSpan, config) {
  let isInitialPageloadComplete = false;
  let hasSeenPageloadSpan = !!activeRootSpan && core.spanToJSON(activeRootSpan).attributes[attributes.SENTRY_OP] === "pageload";
  let hasSeenPopAfterPageload = false;
  let scheduledNavigationHandler = null;
  let lastHandledPathname = null;
  router.subscribe((state) => {
    if (!isInitialPageloadComplete) {
      const currentRootSpan = utils.getActiveRootSpan();
      const isCurrentlyInPageload = currentRootSpan && core.spanToJSON(currentRootSpan).attributes[attributes.SENTRY_OP] === "pageload";
      if (isCurrentlyInPageload) {
        hasSeenPageloadSpan = true;
      } else if (hasSeenPageloadSpan) {
        if (state.historyAction === "POP" && !hasSeenPopAfterPageload) {
          hasSeenPopAfterPageload = true;
        } else {
          isInitialPageloadComplete = true;
        }
      }
    }
    const shouldHandleNavigation = state.historyAction === "PUSH" || state.historyAction === "POP" && isInitialPageloadComplete;
    if (shouldHandleNavigation) {
      const currentLocationKey = computeLocationKey(state.location);
      const navigationHandler = () => {
        if (lastHandledPathname === currentLocationKey) {
          return;
        }
        lastHandledPathname = currentLocationKey;
        scheduledNavigationHandler = null;
        handleNavigation({
          location: state.location,
          routes,
          navigationType: state.historyAction,
          version,
          allRoutes: Array.from(allRoutes),
          config
        });
      };
      if (state.navigation.state !== "idle") {
        if (lastHandledPathname !== currentLocationKey) {
          lastHandledPathname = null;
        }
        if (scheduledNavigationHandler !== null) {
          cancelScheduledCallback(scheduledNavigationHandler);
        }
        scheduledNavigationHandler = scheduleCallback(navigationHandler);
      } else {
        if (scheduledNavigationHandler !== null) {
          cancelScheduledCallback(scheduledNavigationHandler);
          scheduledNavigationHandler = null;
        }
        navigationHandler();
      }
    }
  });
}
function createV6CompatibleWrapCreateBrowserRouter(createRouterFunction, version) {
  return function(routes, opts) {
    const base = getRouterConfig(core.getClient());
    if (!base) {
      debugBuild.DEBUG_BUILD && core.debug.warn(
        `reactRouter${version ? `V${version}` : ""}Instrumentation was unable to wrap the \`createRouter\` function because the React Router browser tracing integration was not set up. Make sure \`Sentry.init()\` runs before the router is created.`
      );
      return createRouterFunction(routes, opts);
    }
    const config = { ...base, basename: opts?.basename || "" };
    addRoutesToAllRoutes(routes);
    if (config.enableAsyncRouteHandlers) {
      for (const route of routes) {
        lazyRoutes.checkRouteForAsyncHandler(route, (r, p, l, s) => processResolvedRoutes(r, config, p, l, s));
      }
    }
    const activeRootSpan = utils.getActiveRootSpan();
    const hasPatchRoutesOnNavigation = opts && "patchRoutesOnNavigation" in opts && typeof opts.patchRoutesOnNavigation === "function";
    if (hasPatchRoutesOnNavigation && activeRootSpan) {
      core.addNonEnumerableProperty(activeRootSpan, "__sentry_may_have_lazy_routes__", true);
      createDeferredLazyRoutePromise(activeRootSpan);
    }
    const wrappedOpts = wrapPatchRoutesOnNavigation(opts, false, activeRootSpan, config);
    const router = createRouterFunction(routes, wrappedOpts);
    if (router.state.historyAction === "POP" && activeRootSpan) {
      updatePageloadTransaction({
        activeRootSpan,
        location: router.state.location,
        routes,
        allRoutes: Array.from(allRoutes),
        config
      });
    }
    setupRouterSubscription(router, routes, version, activeRootSpan, config);
    return router;
  };
}
function createV6CompatibleWrapCreateMemoryRouter(createRouterFunction, version) {
  return function(routes, opts) {
    const base = getRouterConfig(core.getClient());
    if (!base) {
      debugBuild.DEBUG_BUILD && core.debug.warn(
        `reactRouter${version ? `V${version}` : ""}Instrumentation was unable to wrap the \`createMemoryRouter\` function because the React Router browser tracing integration was not set up. Make sure \`Sentry.init()\` runs before the router is created.`
      );
      return createRouterFunction(routes, opts);
    }
    const config = { ...base, basename: opts?.basename || "" };
    addRoutesToAllRoutes(routes);
    if (config.enableAsyncRouteHandlers) {
      for (const route of routes) {
        lazyRoutes.checkRouteForAsyncHandler(route, (r, p, l, s) => processResolvedRoutes(r, config, p, l, s));
      }
    }
    const memoryActiveRootSpanEarly = utils.getActiveRootSpan();
    const hasPatchRoutesOnNavigation = opts && "patchRoutesOnNavigation" in opts && typeof opts.patchRoutesOnNavigation === "function";
    if (hasPatchRoutesOnNavigation && memoryActiveRootSpanEarly) {
      core.addNonEnumerableProperty(memoryActiveRootSpanEarly, "__sentry_may_have_lazy_routes__", true);
      createDeferredLazyRoutePromise(memoryActiveRootSpanEarly);
    }
    const wrappedOpts = wrapPatchRoutesOnNavigation(opts, true, memoryActiveRootSpanEarly, config);
    const router = createRouterFunction(routes, wrappedOpts);
    let initialEntry = void 0;
    const initialEntries = opts?.initialEntries;
    const initialIndex = opts?.initialIndex;
    const hasOnlyOneInitialEntry = initialEntries?.length === 1;
    const hasIndexedEntry = initialIndex !== void 0 && initialEntries?.[initialIndex];
    initialEntry = hasOnlyOneInitialEntry ? initialEntries[0] : hasIndexedEntry ? initialEntries[initialIndex] : void 0;
    const location = initialEntry ? typeof initialEntry === "string" ? { pathname: initialEntry } : initialEntry : router.state.location;
    const memoryActiveRootSpan = utils.getActiveRootSpan();
    if (router.state.historyAction === "POP" && memoryActiveRootSpan) {
      updatePageloadTransaction({
        activeRootSpan: memoryActiveRootSpan,
        location,
        routes,
        allRoutes: Array.from(allRoutes),
        config
      });
    }
    setupRouterSubscription(router, routes, version, memoryActiveRootSpan, config);
    return router;
  };
}
function createReactRouterV6CompatibleTracingIntegration(options, version) {
  const integration = browser.browserTracingIntegration({ ...options, instrumentPageLoad: false, instrumentNavigation: false });
  const {
    useLocation,
    useNavigationType,
    createRoutesFromChildren,
    matchRoutes,
    stripBasename,
    enableAsyncRouteHandlers = false,
    instrumentPageLoad = true,
    instrumentNavigation = true,
    lazyRouteTimeout,
    lazyRouteManifest
  } = options;
  return core.extendIntegration(integration, {
    setup(client) {
      const finalTimeout = options.finalTimeout ?? 3e4;
      const defaultMaxWait = (options.idleTimeout ?? 1e3) * 3;
      const configuredMaxWait = lazyRouteTimeout ?? defaultMaxWait;
      let resolvedLazyRouteTimeout;
      if (configuredMaxWait === Infinity) {
        resolvedLazyRouteTimeout = finalTimeout;
        debugBuild.DEBUG_BUILD && core.debug.log(
          "[React Router] lazyRouteTimeout set to Infinity, capping at finalTimeout:",
          finalTimeout,
          "ms to prevent indefinite hangs"
        );
      } else if (Number.isNaN(configuredMaxWait)) {
        debugBuild.DEBUG_BUILD && core.debug.warn("[React Router] lazyRouteTimeout must be a number, falling back to default:", defaultMaxWait);
        resolvedLazyRouteTimeout = defaultMaxWait;
      } else if (configuredMaxWait < 0) {
        debugBuild.DEBUG_BUILD && core.debug.warn(
          "[React Router] lazyRouteTimeout must be non-negative or Infinity, got:",
          configuredMaxWait,
          "falling back to:",
          defaultMaxWait
        );
        resolvedLazyRouteTimeout = defaultMaxWait;
      } else {
        resolvedLazyRouteTimeout = configuredMaxWait;
      }
      if (typeof useLocation === "function" && typeof useNavigationType === "function" && typeof createRoutesFromChildren === "function" && typeof matchRoutes === "function") {
        reactRouterConfigByClient.set(client, {
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes,
          stripBasename: stripBasename || false,
          enableAsyncRouteHandlers,
          instrumentNavigation,
          lazyRouteTimeout: resolvedLazyRouteTimeout,
          lazyRouteManifest,
          basename: ""
        });
      } else {
        debugBuild.DEBUG_BUILD && core.debug.warn(
          "[React Router] Skipping route instrumentation because `useLocation`, `useNavigationType`, `createRoutesFromChildren` or `matchRoutes` was not provided. Pass them to `reactRouterBrowserTracingIntegration`, or import it from `@sentry/react/react-router` to have them supplied automatically."
        );
      }
    },
    afterAllSetup(client) {
      const initPathName = browser.WINDOW.location?.pathname;
      if (instrumentPageLoad && initPathName) {
        browser.startBrowserTracingPageLoadSpan(client, {
          // With span streaming, span names have to be low cardinality. The route is only resolved
          // once the router renders, which updates the span name then.
          name: core.hasSpanStreamingEnabled(client) ? core.PAGELOAD_SPAN_NAME_FALLBACK : initPathName,
          attributes: {
            [attributes.SENTRY_SEGMENT_NAME_SOURCE]: "url",
            [attributes.SENTRY_OP]: op.PAGELOAD,
            [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: `auto.pageload.react.reactrouter${version ? `_v${version}` : ""}`
          }
        });
      }
    }
  });
}
function createV6CompatibleWrapUseRoutes(origUseRoutes, version) {
  const RouteReporter = ({ config, routes, locationArg }) => {
    const isMountRenderPass = React.useRef(true);
    const location = config.useLocation();
    const navigationType = config.useNavigationType();
    const stableLocationParam = typeof locationArg === "string" || locationArg?.pathname ? locationArg : location;
    useIsomorphicLayoutEffect(() => {
      const added = addRoutesToAllRoutes(routes);
      return () => removeRoutesFromAllRoutes(added);
    });
    useIsomorphicLayoutEffect(() => {
      const normalizedLocation = typeof stableLocationParam === "string" ? { pathname: stableLocationParam } : stableLocationParam;
      if (isMountRenderPass.current) {
        updatePageloadTransaction({
          activeRootSpan: utils.getActiveRootSpan(),
          location: normalizedLocation,
          routes,
          allRoutes: Array.from(allRoutes),
          config
        });
        isMountRenderPass.current = false;
      } else {
        handleNavigation({
          location: normalizedLocation,
          routes,
          navigationType,
          version,
          allRoutes: Array.from(allRoutes),
          config
        });
      }
    }, [navigationType, stableLocationParam]);
    return null;
  };
  const SentryRoutesWrapper = ({
    routes,
    locationArg
  }) => {
    const config = getRouterConfig(core.getClient());
    const routesElement = origUseRoutes(routes, locationArg);
    return /* @__PURE__ */ React.createElement(React.Fragment, null, routesElement, config ? /* @__PURE__ */ React.createElement(RouteReporter, { config, routes, locationArg }) : null);
  };
  return (routes, locationArg) => {
    return /* @__PURE__ */ React.createElement(SentryRoutesWrapper, { routes, locationArg });
  };
}
function wrapPatchRoutesOnNavigation(opts, isMemoryRouter, capturedSpan, config) {
  if (!opts || !("patchRoutesOnNavigation" in opts) || typeof opts.patchRoutesOnNavigation !== "function") {
    return opts || {};
  }
  const originalPatchRoutes = opts.patchRoutesOnNavigation;
  return {
    ...opts,
    patchRoutesOnNavigation: async (args) => {
      const targetPath = args?.path;
      const activeRootSpan = utils.getActiveRootSpan() ?? capturedSpan;
      if (!isMemoryRouter) {
        const originalPatch = args?.patch;
        const matches = args?.matches;
        if (originalPatch) {
          args.patch = (routeId, children) => {
            addRoutesToAllRoutes(children);
            if (matches && matches.length > 0) {
              const leafMatch = matches[matches.length - 1];
              const leafRoute = leafMatch?.route;
              if (leafRoute) {
                const matchingRoute = Array.from(allRoutes).find((route) => {
                  const idMatches = route.id !== void 0 && route.id === routeId;
                  const referenceMatches = route === leafRoute;
                  const pathMatches = route.path !== void 0 && leafRoute.path !== void 0 && route.path === leafRoute.path;
                  return idMatches || referenceMatches || pathMatches;
                });
                if (matchingRoute) {
                  addResolvedRoutesToParent(children, matchingRoute);
                }
              }
            }
            const spanJson = activeRootSpan ? core.spanToJSON(activeRootSpan) : void 0;
            if (targetPath && activeRootSpan && spanJson && !spanJson.end_timestamp && // Span hasn't ended yet
            spanJson.attributes[attributes.SENTRY_OP] === "navigation") {
              updateNavigationSpan(
                activeRootSpan,
                { pathname: targetPath, search: "", hash: "", state: null, key: "default" },
                Array.from(allRoutes),
                true,
                config
              );
            }
            return originalPatch(routeId, children);
          };
        }
      }
      const lazyLoadPromise = (async () => {
        const contextToken = utils.setNavigationContext(targetPath, activeRootSpan);
        let result;
        try {
          result = await originalPatchRoutes(args);
        } finally {
          utils.clearNavigationContext(contextToken);
          if (activeRootSpan) {
            resolveDeferredLazyRoutePromise(activeRootSpan);
          }
        }
        const spanJson = activeRootSpan ? core.spanToJSON(activeRootSpan) : void 0;
        if (activeRootSpan && spanJson && !spanJson.end_timestamp && // Span hasn't ended yet
        spanJson.attributes[attributes.SENTRY_OP] === "navigation") {
          const pathname = targetPath;
          if (pathname) {
            updateNavigationSpan(
              activeRootSpan,
              { pathname, search: "", hash: "", state: null, key: "default" },
              Array.from(allRoutes),
              false,
              config
            );
          }
        }
        return result;
      })();
      if (activeRootSpan) {
        trackLazyRouteLoad(activeRootSpan, lazyLoadPromise);
      }
      return lazyLoadPromise;
    }
  };
}
function handleNavigation(opts) {
  const { location, routes, navigationType, version, config, matches, allRoutes: allRoutes2 } = opts;
  const branches = Array.isArray(matches) ? matches : config.matchRoutes(allRoutes2 || routes, location, config.basename);
  const client = core.getClient();
  if (!client || !config.instrumentNavigation) {
    return;
  }
  const activeRootSpan = utils.getActiveRootSpan();
  if (activeRootSpan && core.spanToJSON(activeRootSpan).attributes[attributes.SENTRY_OP] === "pageload" && navigationType === "POP") {
    return;
  }
  if ((navigationType === "PUSH" || navigationType === "POP") && branches) {
    const [name, source] = utils.resolveRouteNameAndSource(
      location,
      allRoutes2 || routes,
      allRoutes2 || routes,
      branches,
      config
    );
    const locationKey = computeLocationKey(location);
    const trackedNav = activeNavigationSpans.get(client);
    const trackedSpanHasEnded = trackedNav && !trackedNav.isPlaceholder ? !!core.spanToJSON(trackedNav.span).end_timestamp : false;
    const { skip, shouldUpdate } = shouldSkipNavigation(trackedNav, locationKey, name, trackedSpanHasEnded);
    if (skip) {
      if (shouldUpdate && trackedNav) {
        const oldName = trackedNav.routeName;
        if (trackedNav.isPlaceholder) {
          trackedNav.routeName = name;
          debugBuild.DEBUG_BUILD && core.debug.log(
            `[Tracing] Updated placeholder navigation name from "${oldName}" to "${name}" (will apply to real span)`
          );
        } else {
          const isUnparameterizedStreamedNavigation = source !== "route" && core.hasSpanStreamingEnabled(client);
          trackedNav.span.updateName(isUnparameterizedStreamedNavigation ? core.NAVIGATION_SPAN_NAME_FALLBACK : name);
          trackedNav.span.setAttribute(attributes.SENTRY_SEGMENT_NAME_SOURCE, source);
          if (source === "route") {
            trackedNav.span.setAttribute(attributes.URL_TEMPLATE, name);
          }
          core.addNonEnumerableProperty(trackedNav.span, "__sentry_navigation_name_set__", true);
          trackedNav.routeName = name;
          debugBuild.DEBUG_BUILD && core.debug.log(`[Tracing] Updated navigation span name from "${oldName}" to "${name}"`);
        }
      } else {
        debugBuild.DEBUG_BUILD && core.debug.log(`[Tracing] Skipping duplicate navigation for location: ${locationKey}`);
      }
      return;
    }
    const placeholderSpan = { end: () => {
    } };
    const placeholderEntry = {
      span: placeholderSpan,
      routeName: name,
      pathname: location.pathname,
      locationKey,
      isPlaceholder: true
    };
    activeNavigationSpans.set(client, placeholderEntry);
    let navigationSpan;
    try {
      navigationSpan = browser.startBrowserTracingNavigationSpan(client, {
        // Use placeholder's routeName in case it was updated. With span streaming, span names have to
        // be low cardinality, so we can't fall back to the URL.
        name: source === "route" || !core.hasSpanStreamingEnabled(client) ? placeholderEntry.routeName : core.NAVIGATION_SPAN_NAME_FALLBACK,
        attributes: {
          [attributes.SENTRY_SEGMENT_NAME_SOURCE]: source,
          [attributes.SENTRY_OP]: op.NAVIGATION,
          [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: `auto.navigation.react.reactrouter${version ? `_v${version}` : ""}`,
          ...source === "route" && { [attributes.URL_TEMPLATE]: placeholderEntry.routeName }
        }
      });
    } catch (e) {
      activeNavigationSpans.delete(client);
      throw e;
    }
    if (navigationSpan) {
      core.addNonEnumerableProperty(navigationSpan, "__sentry_navigation_pathname__", location.pathname);
      activeNavigationSpans.set(client, {
        span: navigationSpan,
        routeName: placeholderEntry.routeName,
        // Use the (potentially updated) placeholder routeName
        pathname: location.pathname,
        locationKey
      });
      patchSpanEnd(navigationSpan, location, routes, "navigation", config);
    } else {
      activeNavigationSpans.delete(client);
    }
  }
}
function addRoutesToAllRoutes(routes) {
  const added = [];
  routes.forEach((route) => {
    const extractedChildRoutes = getChildRoutesRecursively(route);
    extractedChildRoutes.forEach((r) => {
      allRoutes.add(r);
      added.push(r);
    });
  });
  return added;
}
function removeRoutesFromAllRoutes(routes) {
  routes.forEach((route) => {
    allRoutes.delete(route);
  });
}
function getChildRoutesRecursively(route, allRoutes2 = /* @__PURE__ */ new Set()) {
  if (!allRoutes2.has(route)) {
    allRoutes2.add(route);
    if (route.children && !route.index) {
      route.children.forEach((child) => {
        const childRoutes = getChildRoutesRecursively(child, allRoutes2);
        childRoutes.forEach((r) => {
          allRoutes2.add(r);
        });
      });
    }
  }
  return allRoutes2;
}
function updatePageloadTransaction({
  activeRootSpan,
  location,
  routes,
  config,
  matches,
  allRoutes: allRoutes2
}) {
  const branches = Array.isArray(matches) ? matches : config.matchRoutes(allRoutes2 || routes, location, config.basename);
  if (branches) {
    const [name, source] = utils.resolveRouteNameAndSource(
      location,
      allRoutes2 || routes,
      allRoutes2 || routes,
      branches,
      config
    );
    core.getCurrentScope().setTransactionName(name || "/");
    if (activeRootSpan) {
      const client = core.getClient();
      const isUnparameterizedStreamedPageload = source !== "route" && !!client && core.hasSpanStreamingEnabled(client);
      activeRootSpan.updateName(isUnparameterizedStreamedPageload ? core.PAGELOAD_SPAN_NAME_FALLBACK : name);
      activeRootSpan.setAttribute(attributes.SENTRY_SEGMENT_NAME_SOURCE, source);
      if (source === "route") {
        activeRootSpan.setAttribute(attributes.URL_TEMPLATE, name);
      }
      patchSpanEnd(activeRootSpan, location, routes, "pageload", config);
    }
  } else if (activeRootSpan) {
    patchSpanEnd(activeRootSpan, location, routes, "pageload", config);
  }
}
function shouldUpdateWildcardSpanName(currentName, currentSource, newName, newSource, allowNoCurrentName = false) {
  if (!newName) {
    return false;
  }
  if (!currentName && allowNoCurrentName) {
    return true;
  }
  const hasWildcard = currentName && utils.transactionNameHasWildcard(currentName);
  if (hasWildcard && newSource === "route" && !utils.transactionNameHasWildcard(newName)) {
    return true;
  }
  if (currentSource !== "route" && newSource === "route") {
    return true;
  }
  return false;
}
function tryUpdateSpanNameBeforeEnd(span, spanJson, currentName, location, routes, spanType, allRoutes2, config) {
  try {
    const currentSource = spanJson.attributes[attributes.SENTRY_SEGMENT_NAME_SOURCE];
    if (currentSource === "route" && currentName && !utils.transactionNameHasWildcard(currentName)) {
      return;
    }
    const currentAllRoutes = Array.from(allRoutes2);
    const routesToUse = currentAllRoutes.length > 0 ? currentAllRoutes : routes;
    const branches = config.matchRoutes(routesToUse, location, config.basename);
    if (!branches) {
      return;
    }
    const [name, source] = utils.resolveRouteNameAndSource(location, routesToUse, routesToUse, branches, config);
    const isImprovement = shouldUpdateWildcardSpanName(currentName, currentSource, name, source, true);
    const spanNotEnded = spanType === "pageload" || !spanJson.end_timestamp;
    if (isImprovement && spanNotEnded) {
      const client = core.getClient();
      const isUnparameterizedStreamedSpan = source !== "route" && !!client && core.hasSpanStreamingEnabled(client);
      const fallbackName = spanType === "pageload" ? core.PAGELOAD_SPAN_NAME_FALLBACK : core.NAVIGATION_SPAN_NAME_FALLBACK;
      span.updateName(isUnparameterizedStreamedSpan ? fallbackName : name);
      span.setAttribute(attributes.SENTRY_SEGMENT_NAME_SOURCE, source);
      if (source === "route") {
        span.setAttribute(attributes.URL_TEMPLATE, name);
      }
    }
  } catch (error) {
    debugBuild.DEBUG_BUILD && core.debug.warn(`Error updating span details before ending: ${error}`);
  }
}
function patchSpanEnd(span, location, routes, spanType, config) {
  const patchedPropertyName = `__sentry_${spanType}_end_patched__`;
  const hasEndBeenPatched = span?.[patchedPropertyName];
  if (hasEndBeenPatched || !span.end) {
    return;
  }
  const originalEnd = span.end.bind(span);
  let endCalled = false;
  span.end = function patchedEnd(...args) {
    if (endCalled) {
      return;
    }
    endCalled = true;
    const endTimestamp = args.length > 0 ? args[0] : Date.now() / 1e3;
    const spanJson = core.spanToJSON(span);
    const currentName = spanJson.name;
    const currentSource = spanJson.attributes[attributes.SENTRY_SEGMENT_NAME_SOURCE];
    const cleanupNavigationSpan = () => {
      const client = core.getClient();
      if (client && spanType === "navigation") {
        const trackedNav = activeNavigationSpans.get(client);
        if (trackedNav?.span === span) {
          activeNavigationSpans.delete(client);
        }
      }
    };
    const pendingPromises = pendingLazyRouteLoads.get(span);
    const mayHaveLazyRoutes = span.__sentry_may_have_lazy_routes__;
    const hasPendingOrMayHaveLazyRoutes = pendingPromises && pendingPromises.size > 0 || mayHaveLazyRoutes;
    const shouldWaitForLazyRoutes = hasPendingOrMayHaveLazyRoutes && currentName && (utils.transactionNameHasWildcard(currentName) || currentSource !== "route");
    if (shouldWaitForLazyRoutes) {
      if (config.lazyRouteTimeout === 0) {
        tryUpdateSpanNameBeforeEnd(span, spanJson, currentName, location, routes, spanType, allRoutes, config);
        cleanupNavigationSpan();
        originalEnd(endTimestamp);
        return;
      }
      const timeoutPromise = new Promise((r) => setTimeout(r, config.lazyRouteTimeout));
      let waitPromise;
      if (pendingPromises && pendingPromises.size > 0) {
        const allSettled = Promise.allSettled(pendingPromises).then(() => {
        });
        waitPromise = config.lazyRouteTimeout === Infinity ? allSettled : Promise.race([allSettled, timeoutPromise]);
      } else {
        waitPromise = timeoutPromise;
      }
      waitPromise.then(() => {
        const updatedSpanJson = core.spanToJSON(span);
        tryUpdateSpanNameBeforeEnd(
          span,
          updatedSpanJson,
          updatedSpanJson.name,
          location,
          routes,
          spanType,
          allRoutes,
          config
        );
        cleanupNavigationSpan();
        originalEnd(endTimestamp);
      }).catch(() => {
        cleanupNavigationSpan();
        originalEnd(endTimestamp);
      });
      return;
    }
    tryUpdateSpanNameBeforeEnd(span, spanJson, currentName, location, routes, spanType, allRoutes, config);
    cleanupNavigationSpan();
    originalEnd(endTimestamp);
  };
  core.addNonEnumerableProperty(span, patchedPropertyName, true);
}
function createV6CompatibleWithSentryReactRouterRouting(Routes, version) {
  const RouteReporter = ({
    config,
    routeChildren
  }) => {
    const isMountRenderPass = React.useRef(true);
    const location = config.useLocation();
    const navigationType = config.useNavigationType();
    const routes = config.createRoutesFromChildren(
      routeChildren
    );
    useIsomorphicLayoutEffect(() => {
      const added = addRoutesToAllRoutes(routes);
      return () => removeRoutesFromAllRoutes(added);
    });
    useIsomorphicLayoutEffect(
      () => {
        if (isMountRenderPass.current) {
          updatePageloadTransaction({
            activeRootSpan: utils.getActiveRootSpan(),
            location,
            routes,
            allRoutes: Array.from(allRoutes),
            config
          });
          isMountRenderPass.current = false;
        } else {
          handleNavigation({
            location,
            routes,
            navigationType,
            version,
            allRoutes: Array.from(allRoutes),
            config
          });
        }
      },
      // Re-run only on location/navigation changes, not children changes
      [location, navigationType]
    );
    return null;
  };
  const SentryRoutes = (props) => {
    const config = getRouterConfig(core.getClient());
    return /* @__PURE__ */ React.createElement(
      React.Fragment,
      null,
      // @ts-expect-error Setting more specific React Component typing for `R` generic above
      // will break advanced type inference done by react router params
      /* @__PURE__ */ React.createElement(Routes, { ...props }),
      config ? /* @__PURE__ */ React.createElement(RouteReporter, { config, routeChildren: props.children }) : null
    );
  };
  hoistNonReactStatics.hoistNonReactStatics(SentryRoutes, Routes);
  return SentryRoutes;
}

exports.addResolvedRoutesToParent = addResolvedRoutesToParent;
exports.addRoutesToAllRoutes = addRoutesToAllRoutes;
exports.allRoutes = allRoutes;
exports.computeLocationKey = computeLocationKey;
exports.createReactRouterV6CompatibleTracingIntegration = createReactRouterV6CompatibleTracingIntegration;
exports.createV6CompatibleWithSentryReactRouterRouting = createV6CompatibleWithSentryReactRouterRouting;
exports.createV6CompatibleWrapCreateBrowserRouter = createV6CompatibleWrapCreateBrowserRouter;
exports.createV6CompatibleWrapCreateMemoryRouter = createV6CompatibleWrapCreateMemoryRouter;
exports.createV6CompatibleWrapUseRoutes = createV6CompatibleWrapUseRoutes;
exports.handleNavigation = handleNavigation;
exports.processResolvedRoutes = processResolvedRoutes;
exports.shouldSkipNavigation = shouldSkipNavigation;
exports.updateNavigationSpan = updateNavigationSpan;
//# sourceMappingURL=instrumentation.js.map
