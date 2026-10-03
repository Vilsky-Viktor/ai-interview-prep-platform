import { getSanitizedUrlStringFromUrlObject, parseStringToURLObject } from '@sentry/core';

const HeaderKeys = {
  FORWARDED_PROTO: "x-forwarded-proto",
  FORWARDED_HOST: "x-forwarded-host",
  HOST: "host",
  REFERER: "referer"
};
function substituteRouteParams(path, params) {
  return path;
}
function sanitizeRoutePath(path) {
  const cleanedSegments = path.split("/").filter((segment) => segment && !(segment.startsWith("(") && segment.endsWith(")")));
  return cleanedSegments.length > 0 ? `/${cleanedSegments.join("/")}` : "/";
}
function buildUrlFromComponentRoute(componentRoute, params, headersDict, pathname) {
  const parameterizedPath = substituteRouteParams(componentRoute);
  const path = pathname ?? sanitizeRoutePath(parameterizedPath);
  const protocol = headersDict?.[HeaderKeys.FORWARDED_PROTO];
  const host = headersDict?.[HeaderKeys.FORWARDED_HOST] || headersDict?.[HeaderKeys.HOST];
  if (!protocol || !host) {
    return path;
  }
  const fullUrl = `${protocol}://${host}${path}`;
  const urlObject = parseStringToURLObject(fullUrl);
  if (!urlObject) {
    return path;
  }
  return getSanitizedUrlStringFromUrlObject(urlObject);
}
function extractSanitizedUrlFromRefererHeader(headersDict) {
  const referer = headersDict?.[HeaderKeys.REFERER];
  if (!referer) {
    return void 0;
  }
  try {
    const refererUrl = new URL(referer);
    return getSanitizedUrlStringFromUrlObject(refererUrl);
  } catch {
    return void 0;
  }
}
function getSanitizedRequestUrl(componentRoute, params, headersDict, pathname) {
  const refererUrl = extractSanitizedUrlFromRefererHeader(headersDict);
  if (refererUrl) {
    return refererUrl;
  }
  return buildUrlFromComponentRoute(componentRoute, params, headersDict, pathname);
}

export { buildUrlFromComponentRoute, extractSanitizedUrlFromRefererHeader, getSanitizedRequestUrl, sanitizeRoutePath, substituteRouteParams };
//# sourceMappingURL=urls.js.map
