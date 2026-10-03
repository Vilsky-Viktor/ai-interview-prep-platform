Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const core = require('@sentry/core');
const browserUtils = require('@sentry/browser-utils');
const attributes = require('@sentry/conventions/attributes');

const INTEGRATION_NAME = "GraphQLClient";
const _graphqlClientIntegration = ((options) => {
  return {
    name: INTEGRATION_NAME,
    setup(client) {
      _updateSpanWithGraphQLData(client, options);
      _updateBreadcrumbWithGraphQLData(client, options);
    }
  };
});
function _updateSpanWithGraphQLData(client, options) {
  client.on("beforeOutgoingRequestSpan", (span, hint) => {
    const spanJSON = core.spanToJSON(span);
    const spanAttributes = spanJSON.attributes;
    const spanOp = spanAttributes[attributes.SENTRY_OP];
    const isHttpClientSpan = spanOp === "http.client";
    if (!isHttpClientSpan) {
      return;
    }
    const httpUrl = spanAttributes[attributes.URL_FULL];
    const httpMethod = spanAttributes[core.SEMANTIC_ATTRIBUTE_HTTP_REQUEST_METHOD] || spanAttributes[attributes.HTTP_METHOD];
    if (!core.isString(httpUrl) || !core.isString(httpMethod)) {
      return;
    }
    const { endpoints } = options;
    const isTracedGraphqlEndpoint = core.stringMatchesSomePattern(httpUrl, endpoints);
    const payload = getRequestPayloadXhrOrFetch(hint);
    if (isTracedGraphqlEndpoint && payload) {
      const graphqlBody = getGraphQLRequestPayload(payload);
      if (graphqlBody) {
        if (!core.hasSpanStreamingEnabled(client)) {
          span.updateName(`${httpMethod} ${httpUrl} (${_getGraphQLOperation(graphqlBody)})`);
        }
        const { operationName, operationType } = _getGraphQLOperationDetails(graphqlBody);
        span.setAttribute(attributes.GRAPHQL_OPERATION_NAME, operationName);
        span.setAttribute(attributes.GRAPHQL_OPERATION_TYPE, operationType);
        if (isStandardRequest(graphqlBody) && client.getDataCollectionOptions().graphQL.document === true) {
          span.setAttribute(attributes.GRAPHQL_DOCUMENT, graphqlBody.query);
        }
        if (isPersistedRequest(graphqlBody)) {
          span.setAttribute("graphql.persisted_query.hash.sha256", graphqlBody.extensions.persistedQuery.sha256Hash);
          span.setAttribute("graphql.persisted_query.version", graphqlBody.extensions.persistedQuery.version);
        }
      }
    }
  });
}
function _updateBreadcrumbWithGraphQLData(client, options) {
  client.on("beforeOutgoingRequestBreadcrumb", (breadcrumb, handlerData) => {
    const { category, type, data } = breadcrumb;
    const isFetch = category === "fetch";
    const isXhr = category === "xhr";
    const isHttpBreadcrumb = type === "http";
    if (isHttpBreadcrumb && (isFetch || isXhr)) {
      const httpUrl = data?.url;
      const { endpoints } = options;
      const isTracedGraphqlEndpoint = core.stringMatchesSomePattern(httpUrl, endpoints);
      const payload = getRequestPayloadXhrOrFetch(handlerData);
      if (isTracedGraphqlEndpoint && data && payload) {
        const graphqlBody = getGraphQLRequestPayload(payload);
        if (!data.graphql && graphqlBody) {
          const operationInfo = _getGraphQLOperation(graphqlBody);
          data["graphql.operation"] = operationInfo;
          if (isStandardRequest(graphqlBody) && client.getDataCollectionOptions().graphQL.document === true) {
            data[attributes.GRAPHQL_DOCUMENT] = graphqlBody.query;
          }
          if (isPersistedRequest(graphqlBody)) {
            data["graphql.persisted_query.hash.sha256"] = graphqlBody.extensions.persistedQuery.sha256Hash;
            data["graphql.persisted_query.version"] = graphqlBody.extensions.persistedQuery.version;
          }
        }
      }
    }
  });
}
function _getGraphQLOperationDetails(requestBody) {
  if (isPersistedRequest(requestBody)) {
    return { operationName: requestBody.operationName, operationType: void 0 };
  }
  if (isStandardRequest(requestBody)) {
    const { query: graphqlQuery, operationName: graphqlOperationName } = requestBody;
    const { operationName = graphqlOperationName, operationType } = parseGraphQLQuery(graphqlQuery);
    return { operationName, operationType };
  }
  return { operationName: void 0, operationType: void 0 };
}
function _getGraphQLOperation(requestBody) {
  if (isPersistedRequest(requestBody)) {
    return `persisted ${requestBody.operationName}`;
  }
  if (isStandardRequest(requestBody)) {
    const { operationName, operationType } = _getGraphQLOperationDetails(requestBody);
    return operationName ? `${operationType} ${operationName}` : `${operationType}`;
  }
  return "unknown";
}
function getRequestPayloadXhrOrFetch(hint) {
  const isXhr = "xhr" in hint;
  let body;
  if (isXhr) {
    const sentryXhrData = hint.xhr[browserUtils.SENTRY_XHR_DATA_KEY];
    body = sentryXhrData && browserUtils.getBodyString(sentryXhrData.body)[0];
  } else {
    const sentryFetchData = browserUtils.getFetchRequestArgBody(hint.input);
    body = browserUtils.getBodyString(sentryFetchData)[0];
  }
  return body;
}
function parseGraphQLQuery(query) {
  const namedQueryRe = /^(?:\s*)(query|mutation|subscription)(?:\s*)(\w+)(?:\s*)[{(]/;
  const unnamedQueryRe = /^(?:\s*)(query|mutation|subscription)(?:\s*)[{(]/;
  const namedMatch = query.match(namedQueryRe);
  if (namedMatch) {
    return {
      operationType: namedMatch[1],
      operationName: namedMatch[2]
    };
  }
  const unnamedMatch = query.match(unnamedQueryRe);
  if (unnamedMatch) {
    return {
      operationType: unnamedMatch[1],
      operationName: void 0
    };
  }
  return {
    operationType: void 0,
    operationName: void 0
  };
}
function isStandardRequest(payload) {
  return core.isObjectLike(payload) && typeof payload.query === "string";
}
function isPersistedRequest(payload) {
  return core.isObjectLike(payload) && typeof payload.operationName === "string" && core.isObjectLike(payload.extensions) && core.isObjectLike(payload.extensions.persistedQuery) && typeof payload.extensions.persistedQuery.sha256Hash === "string" && typeof payload.extensions.persistedQuery.version === "number";
}
function getGraphQLRequestPayload(payload) {
  try {
    const requestBody = JSON.parse(payload);
    if (isStandardRequest(requestBody) || isPersistedRequest(requestBody)) {
      return requestBody;
    }
    return void 0;
  } catch {
    return void 0;
  }
}
const graphqlClientIntegration = core.defineIntegration(_graphqlClientIntegration);

exports._getGraphQLOperation = _getGraphQLOperation;
exports.getGraphQLRequestPayload = getGraphQLRequestPayload;
exports.getRequestPayloadXhrOrFetch = getRequestPayloadXhrOrFetch;
exports.graphqlClientIntegration = graphqlClientIntegration;
exports.parseGraphQLQuery = parseGraphQLQuery;
//# sourceMappingURL=graphqlClient.js.map
