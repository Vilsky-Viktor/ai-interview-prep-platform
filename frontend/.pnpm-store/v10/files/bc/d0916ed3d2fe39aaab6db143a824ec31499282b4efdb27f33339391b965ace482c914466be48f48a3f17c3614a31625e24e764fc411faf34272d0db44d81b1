import { defineIntegration, spanToJSON, SEMANTIC_ATTRIBUTE_HTTP_REQUEST_METHOD, isString, stringMatchesSomePattern, hasSpanStreamingEnabled, isObjectLike } from '@sentry/core';
import { SENTRY_XHR_DATA_KEY, getBodyString, getFetchRequestArgBody } from '@sentry/browser-utils';
import { SENTRY_OP, URL_FULL, HTTP_METHOD, GRAPHQL_OPERATION_NAME, GRAPHQL_OPERATION_TYPE, GRAPHQL_DOCUMENT } from '@sentry/conventions/attributes';

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
    const spanJSON = spanToJSON(span);
    const spanAttributes = spanJSON.attributes;
    const spanOp = spanAttributes[SENTRY_OP];
    const isHttpClientSpan = spanOp === "http.client";
    if (!isHttpClientSpan) {
      return;
    }
    const httpUrl = spanAttributes[URL_FULL];
    const httpMethod = spanAttributes[SEMANTIC_ATTRIBUTE_HTTP_REQUEST_METHOD] || spanAttributes[HTTP_METHOD];
    if (!isString(httpUrl) || !isString(httpMethod)) {
      return;
    }
    const { endpoints } = options;
    const isTracedGraphqlEndpoint = stringMatchesSomePattern(httpUrl, endpoints);
    const payload = getRequestPayloadXhrOrFetch(hint);
    if (isTracedGraphqlEndpoint && payload) {
      const graphqlBody = getGraphQLRequestPayload(payload);
      if (graphqlBody) {
        if (!hasSpanStreamingEnabled(client)) {
          span.updateName(`${httpMethod} ${httpUrl} (${_getGraphQLOperation(graphqlBody)})`);
        }
        const { operationName, operationType } = _getGraphQLOperationDetails(graphqlBody);
        span.setAttribute(GRAPHQL_OPERATION_NAME, operationName);
        span.setAttribute(GRAPHQL_OPERATION_TYPE, operationType);
        if (isStandardRequest(graphqlBody) && client.getDataCollectionOptions().graphQL.document === true) {
          span.setAttribute(GRAPHQL_DOCUMENT, graphqlBody.query);
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
      const isTracedGraphqlEndpoint = stringMatchesSomePattern(httpUrl, endpoints);
      const payload = getRequestPayloadXhrOrFetch(handlerData);
      if (isTracedGraphqlEndpoint && data && payload) {
        const graphqlBody = getGraphQLRequestPayload(payload);
        if (!data.graphql && graphqlBody) {
          const operationInfo = _getGraphQLOperation(graphqlBody);
          data["graphql.operation"] = operationInfo;
          if (isStandardRequest(graphqlBody) && client.getDataCollectionOptions().graphQL.document === true) {
            data[GRAPHQL_DOCUMENT] = graphqlBody.query;
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
    const sentryXhrData = hint.xhr[SENTRY_XHR_DATA_KEY];
    body = sentryXhrData && getBodyString(sentryXhrData.body)[0];
  } else {
    const sentryFetchData = getFetchRequestArgBody(hint.input);
    body = getBodyString(sentryFetchData)[0];
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
  return isObjectLike(payload) && typeof payload.query === "string";
}
function isPersistedRequest(payload) {
  return isObjectLike(payload) && typeof payload.operationName === "string" && isObjectLike(payload.extensions) && isObjectLike(payload.extensions.persistedQuery) && typeof payload.extensions.persistedQuery.sha256Hash === "string" && typeof payload.extensions.persistedQuery.version === "number";
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
const graphqlClientIntegration = defineIntegration(_graphqlClientIntegration);

export { _getGraphQLOperation, getGraphQLRequestPayload, getRequestPayloadXhrOrFetch, graphqlClientIntegration, parseGraphQLQuery };
//# sourceMappingURL=graphqlClient.js.map
