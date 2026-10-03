import { WINDOW } from './types.js';

const BOT_USER_AGENT_RE = /Googlebot|Google-InspectionTool|Storebot-Google|Bingbot|Slurp|DuckDuckBot|Baiduspider|YandexBot|Facebot|facebookexternalhit|LinkedInBot|Twitterbot|Applebot/i;
function isBotUserAgent() {
  const nav = WINDOW.navigator;
  if (!nav?.userAgent) {
    return false;
  }
  return BOT_USER_AGENT_RE.test(nav.userAgent);
}

export { isBotUserAgent };
//# sourceMappingURL=isBotUserAgent.js.map
