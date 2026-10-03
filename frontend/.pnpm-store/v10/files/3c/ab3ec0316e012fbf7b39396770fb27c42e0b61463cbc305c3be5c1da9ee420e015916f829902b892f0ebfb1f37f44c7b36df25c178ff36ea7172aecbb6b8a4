import { GLOBAL_OBJ, getClient, getCurrentScope, captureFeedback, isBrowser, debug, addIntegration, getIsolationScope, getGlobalScope } from '@sentry/core';

const WINDOW = GLOBAL_OBJ;
const DOCUMENT = WINDOW.document;
const NAVIGATOR = WINDOW.navigator;
const TRIGGER_LABEL = "Report a Bug";
const CANCEL_BUTTON_LABEL = "Cancel";
const SUBMIT_BUTTON_LABEL = "Send Bug Report";
const CONFIRM_BUTTON_LABEL = "Confirm";
const FORM_TITLE = "Report a Bug";
const EMAIL_PLACEHOLDER = "your.email@example.org";
const EMAIL_LABEL = "Email";
const MESSAGE_PLACEHOLDER = "What's the bug? What did you expect?";
const MESSAGE_LABEL = "Description";
const NAME_PLACEHOLDER = "Your Name";
const NAME_LABEL = "Name";
const SUCCESS_MESSAGE_TEXT = "Thank you for your report!";
const IS_REQUIRED_LABEL = "(required)";
const ADD_SCREENSHOT_LABEL = "Add a screenshot";
const REMOVE_SCREENSHOT_LABEL = "Remove screenshot";
const HIGHLIGHT_TOOL_TEXT = "Highlight";
const HIDE_TOOL_TEXT = "Hide";
const REMOVE_HIGHLIGHT_TEXT = "Remove";
const ERROR_EMPTY_MESSAGE_TEXT = "Unable to submit feedback with empty message";
const ERROR_NO_CLIENT_TEXT = "No client setup, cannot send feedback.";
const ERROR_TIMEOUT_TEXT = "Unable to determine if Feedback was correctly sent.";
const ERROR_FORBIDDEN_TEXT = "Unable to send feedback. This could be because this domain is not in your list of allowed domains.";
const ERROR_GENERIC_TEXT = "Unable to send feedback. This could be because of network issues, or because you are using an ad-blocker.";
const FEEDBACK_WIDGET_SOURCE = "widget";
const FEEDBACK_API_SOURCE = "api";
const SUCCESS_MESSAGE_TIMEOUT = 5e3;

const DEFAULT_MESSAGES = {
  ERROR_EMPTY_MESSAGE: ERROR_EMPTY_MESSAGE_TEXT,
  ERROR_NO_CLIENT: ERROR_NO_CLIENT_TEXT,
  ERROR_TIMEOUT: ERROR_TIMEOUT_TEXT,
  ERROR_FORBIDDEN: ERROR_FORBIDDEN_TEXT,
  ERROR_GENERIC: ERROR_GENERIC_TEXT
};
function resolveFeedbackErrorMessage(code, messages) {
  return messages?.[code] ?? DEFAULT_MESSAGES[code];
}
function createFeedbackError(code, messages) {
  return new Error(resolveFeedbackErrorMessage(code, messages));
}

const sendFeedback = (params, hint = { includeReplay: true }) => {
  const errorMessages = hint.errorMessages;
  if (!params.message) {
    throw createFeedbackError("ERROR_EMPTY_MESSAGE", errorMessages);
  }
  const client = getClient();
  if (!client) {
    throw createFeedbackError("ERROR_NO_CLIENT", errorMessages);
  }
  if (params.tags && Object.keys(params.tags).length) {
    getCurrentScope().setTags(params.tags);
  }
  const eventId = captureFeedback(
    {
      source: FEEDBACK_API_SOURCE,
      url: _getLocationHref(),
      ...params
    },
    hint
  );
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      cleanup();
      reject(createFeedbackError("ERROR_TIMEOUT", errorMessages));
    }, 3e4);
    const cleanup = client.on("afterSendEvent", (event, response) => {
      if (event.event_id !== eventId) {
        return;
      }
      clearTimeout(timeout);
      cleanup();
      if (response?.statusCode && response.statusCode >= 200 && response.statusCode < 300) {
        return resolve(eventId);
      }
      if (response?.statusCode === 403) {
        return reject(createFeedbackError("ERROR_FORBIDDEN", errorMessages));
      }
      return reject(createFeedbackError("ERROR_GENERIC", errorMessages));
    });
  });
};
function _getLocationHref() {
  try {
    return WINDOW.document.location.href;
  } catch {
    return "";
  }
}

const DEBUG_BUILD = (typeof __SENTRY_DEBUG__ === 'undefined' || __SENTRY_DEBUG__);

function isScreenshotSupported() {
  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(NAVIGATOR.userAgent)) {
    return false;
  }
  if (/Macintosh/i.test(NAVIGATOR.userAgent) && NAVIGATOR.maxTouchPoints && NAVIGATOR.maxTouchPoints > 1) {
    return false;
  }
  if (!isSecureContext) {
    return false;
  }
  return true;
}

function mergeOptions(defaultOptions, optionOverrides) {
  return {
    ...defaultOptions,
    ...optionOverrides,
    tags: {
      ...defaultOptions.tags,
      ...optionOverrides.tags
    },
    onFormOpen: () => {
      optionOverrides.onFormOpen?.();
      defaultOptions.onFormOpen?.();
    },
    onFormClose: () => {
      optionOverrides.onFormClose?.();
      defaultOptions.onFormClose?.();
    },
    onSubmitSuccess: (data, eventId) => {
      optionOverrides.onSubmitSuccess?.(data, eventId);
      defaultOptions.onSubmitSuccess?.(data, eventId);
    },
    onSubmitError: (error) => {
      optionOverrides.onSubmitError?.(error);
      defaultOptions.onSubmitError?.(error);
    },
    onFormSubmitted: () => {
      optionOverrides.onFormSubmitted?.();
      defaultOptions.onFormSubmitted?.();
    },
    themeDark: {
      ...defaultOptions.themeDark,
      ...optionOverrides.themeDark
    },
    themeLight: {
      ...defaultOptions.themeLight,
      ...optionOverrides.themeLight
    }
  };
}

function createActorStyles(styleNonce) {
  const style = DOCUMENT.createElement("style");
  style.textContent = `
.widget__actor {
  position: fixed;
  z-index: var(--z-index);
  margin: var(--page-margin);
  inset: var(--actor-inset);

  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;

  font-family: inherit;
  font-size: var(--font-size);
  font-weight: 600;
  line-height: 1.14em;
  text-decoration: none;

  background: var(--actor-background, var(--background));
  border-radius: var(--actor-border-radius, 1.7em/50%);
  border: var(--actor-border, var(--border));
  box-shadow: var(--actor-box-shadow, var(--box-shadow));
  color: var(--actor-color, var(--foreground));
  fill: var(--actor-color, var(--foreground));
  cursor: pointer;
  opacity: 1;
  transition: transform 0.2s ease-in-out;
  transform: translate(0, 0) scale(1);
}
.widget__actor[aria-hidden="true"] {
  opacity: 0;
  pointer-events: none;
  visibility: hidden;
  transform: translate(0, 16px) scale(0.98);
}

.widget__actor:hover {
  background: var(--actor-hover-background, var(--background));
  filter: var(--interactive-filter);
}

.widget__actor svg {
  width: 1.14em;
  height: 1.14em;
}

@media (max-width: 600px) {
  .widget__actor span {
    display: none;
  }
}
`;
  if (styleNonce) {
    style.setAttribute("nonce", styleNonce);
  }
  return style;
}

function setAttributesNS(el, attributes) {
  Object.entries(attributes).forEach(([key, val]) => {
    el.setAttributeNS(null, key, val);
  });
  return el;
}

const SIZE = 20;
const XMLNS$2 = "http://www.w3.org/2000/svg";
function FeedbackIcon() {
  const createElementNS = (tagName) => WINDOW.document.createElementNS(XMLNS$2, tagName);
  const svg = setAttributesNS(createElementNS("svg"), {
    width: `${SIZE}`,
    height: `${SIZE}`,
    viewBox: `0 0 ${SIZE} ${SIZE}`,
    fill: "var(--actor-color, var(--foreground))"
  });
  const g = setAttributesNS(createElementNS("g"), {
    clipPath: "url(#clip0_57_80)"
  });
  const path = setAttributesNS(createElementNS("path"), {
    ["fill-rule"]: "evenodd",
    ["clip-rule"]: "evenodd",
    d: "M15.6622 15H12.3997C12.2129 14.9959 12.031 14.9396 11.8747 14.8375L8.04965 12.2H7.49956V19.1C7.4875 19.3348 7.3888 19.5568 7.22256 19.723C7.05632 19.8892 6.83435 19.9879 6.59956 20H2.04956C1.80193 19.9968 1.56535 19.8969 1.39023 19.7218C1.21511 19.5467 1.1153 19.3101 1.11206 19.0625V12.2H0.949652C0.824431 12.2017 0.700142 12.1783 0.584123 12.1311C0.468104 12.084 0.362708 12.014 0.274155 11.9255C0.185602 11.8369 0.115689 11.7315 0.0685419 11.6155C0.0213952 11.4995 -0.00202913 11.3752 -0.00034808 11.25V3.75C-0.00900498 3.62067 0.0092504 3.49095 0.0532651 3.36904C0.0972798 3.24712 0.166097 3.13566 0.255372 3.04168C0.344646 2.94771 0.452437 2.87327 0.571937 2.82307C0.691437 2.77286 0.82005 2.74798 0.949652 2.75H8.04965L11.8747 0.1625C12.031 0.0603649 12.2129 0.00407221 12.3997 0H15.6622C15.9098 0.00323746 16.1464 0.103049 16.3215 0.278167C16.4966 0.453286 16.5964 0.689866 16.5997 0.9375V3.25269C17.3969 3.42959 18.1345 3.83026 18.7211 4.41679C19.5322 5.22788 19.9878 6.32796 19.9878 7.47502C19.9878 8.62209 19.5322 9.72217 18.7211 10.5333C18.1345 11.1198 17.3969 11.5205 16.5997 11.6974V14.0125C16.6047 14.1393 16.5842 14.2659 16.5395 14.3847C16.4948 14.5035 16.4268 14.6121 16.3394 14.7042C16.252 14.7962 16.147 14.8698 16.0307 14.9206C15.9144 14.9714 15.7891 14.9984 15.6622 15ZM1.89695 10.325H1.88715V4.625H8.33715C8.52423 4.62301 8.70666 4.56654 8.86215 4.4625L12.6872 1.875H14.7247V13.125H12.6872L8.86215 10.4875C8.70666 10.3835 8.52423 10.327 8.33715 10.325H2.20217C2.15205 10.3167 2.10102 10.3125 2.04956 10.3125C1.9981 10.3125 1.94708 10.3167 1.89695 10.325ZM2.98706 12.2V18.1625H5.66206V12.2H2.98706ZM16.5997 9.93612V5.01393C16.6536 5.02355 16.7072 5.03495 16.7605 5.04814C17.1202 5.13709 17.4556 5.30487 17.7425 5.53934C18.0293 5.77381 18.2605 6.06912 18.4192 6.40389C18.578 6.73866 18.6603 7.10452 18.6603 7.47502C18.6603 7.84552 18.578 8.21139 18.4192 8.54616C18.2605 8.88093 18.0293 9.17624 17.7425 9.41071C17.4556 9.64518 17.1202 9.81296 16.7605 9.90191C16.7072 9.91509 16.6536 9.9265 16.5997 9.93612Z"
  });
  svg.appendChild(g).appendChild(path);
  const speakerDefs = createElementNS("defs");
  const speakerClipPathDef = setAttributesNS(createElementNS("clipPath"), {
    id: "clip0_57_80"
  });
  const speakerRect = setAttributesNS(createElementNS("rect"), {
    width: `${SIZE}`,
    height: `${SIZE}`,
    fill: "white"
  });
  speakerClipPathDef.appendChild(speakerRect);
  speakerDefs.appendChild(speakerClipPathDef);
  svg.appendChild(speakerDefs).appendChild(speakerClipPathDef).appendChild(speakerRect);
  return svg;
}

function Actor({ triggerLabel, triggerAriaLabel, shadow, styleNonce }) {
  const el = DOCUMENT.createElement("button");
  el.type = "button";
  el.className = "widget__actor";
  el.ariaHidden = "false";
  el.ariaLabel = triggerAriaLabel || triggerLabel || TRIGGER_LABEL;
  el.appendChild(FeedbackIcon());
  if (triggerLabel) {
    const label = DOCUMENT.createElement("span");
    label.appendChild(DOCUMENT.createTextNode(triggerLabel));
    el.appendChild(label);
  }
  const style = createActorStyles(styleNonce);
  return {
    el,
    appendToDom() {
      shadow.appendChild(style);
      shadow.appendChild(el);
    },
    removeFromDom() {
      el.remove();
      style.remove();
    },
    show() {
      el.ariaHidden = "false";
    },
    hide() {
      el.ariaHidden = "true";
    }
  };
}

const PURPLE = "rgba(88, 74, 192, 1)";
const DEFAULT_LIGHT = {
  foreground: "#2b2233",
  background: "#ffffff",
  accentForeground: "white",
  accentBackground: PURPLE,
  successColor: "#268d75",
  errorColor: "#df3338",
  border: "1.5px solid rgba(41, 35, 47, 0.13)",
  boxShadow: "0px 4px 24px 0px rgba(43, 34, 51, 0.12)",
  outline: "1px auto var(--accent-background)",
  interactiveFilter: "brightness(95%)"
};
const DEFAULT_DARK = {
  foreground: "#ebe6ef",
  background: "#29232f",
  accentForeground: "white",
  accentBackground: PURPLE,
  successColor: "#2da98c",
  errorColor: "#f55459",
  border: "1.5px solid rgba(235, 230, 239, 0.15)",
  boxShadow: "0px 4px 24px 0px rgba(43, 34, 51, 0.12)",
  outline: "1px auto var(--accent-background)",
  interactiveFilter: "brightness(150%)"
};
function getThemedCssVariables(theme) {
  return `
  --foreground: ${theme.foreground};
  --background: ${theme.background};
  --accent-foreground: ${theme.accentForeground};
  --accent-background: ${theme.accentBackground};
  --success-color: ${theme.successColor};
  --error-color: ${theme.errorColor};
  --border: ${theme.border};
  --box-shadow: ${theme.boxShadow};
  --outline: ${theme.outline};
  --interactive-filter: ${theme.interactiveFilter};
  `;
}
function createMainStyles({
  colorScheme,
  themeDark,
  themeLight,
  styleNonce
}) {
  const style = DOCUMENT.createElement("style");
  style.textContent = `
:host {
  --font-family: system-ui, 'Helvetica Neue', Arial, sans-serif;
  --font-size: 14px;
  --z-index: 100000;

  --page-margin: 16px;
  --inset: auto 0 0 auto;
  --actor-inset: var(--inset);

  font-family: var(--font-family);
  font-size: var(--font-size);

  ${colorScheme !== "system" ? `color-scheme: only ${colorScheme};` : ""}

  ${getThemedCssVariables(
    colorScheme === "dark" ? { ...DEFAULT_DARK, ...themeDark } : { ...DEFAULT_LIGHT, ...themeLight }
  )}
}

${colorScheme === "system" ? `
@media (prefers-color-scheme: dark) {
  :host {
    color-scheme: only dark;

    ${getThemedCssVariables({ ...DEFAULT_DARK, ...themeDark })}
  }
}` : ""}
`;
  if (styleNonce) {
    style.setAttribute("nonce", styleNonce);
  }
  return style;
}

const buildFeedbackIntegration = ({
  lazyLoadIntegration,
  getModalIntegration,
  getScreenshotIntegration
}) => {
  const feedbackIntegration = (({
    // FeedbackGeneralConfiguration
    id = "sentry-feedback",
    autoInject = true,
    showBranding = true,
    isEmailRequired = false,
    isNameRequired = false,
    showEmail = true,
    showName = true,
    enableScreenshot = true,
    useSentryUser = {
      email: "email",
      name: "username"
    },
    tags,
    styleNonce,
    scriptNonce,
    // FeedbackThemeConfiguration
    colorScheme = "system",
    themeLight = {},
    themeDark = {},
    // FeedbackTextConfiguration
    addScreenshotButtonLabel = ADD_SCREENSHOT_LABEL,
    cancelButtonLabel = CANCEL_BUTTON_LABEL,
    confirmButtonLabel = CONFIRM_BUTTON_LABEL,
    emailLabel = EMAIL_LABEL,
    emailPlaceholder = EMAIL_PLACEHOLDER,
    formTitle = FORM_TITLE,
    isRequiredLabel = IS_REQUIRED_LABEL,
    messageLabel = MESSAGE_LABEL,
    messagePlaceholder = MESSAGE_PLACEHOLDER,
    nameLabel = NAME_LABEL,
    namePlaceholder = NAME_PLACEHOLDER,
    removeScreenshotButtonLabel = REMOVE_SCREENSHOT_LABEL,
    submitButtonLabel = SUBMIT_BUTTON_LABEL,
    successMessageText = SUCCESS_MESSAGE_TEXT,
    triggerLabel = TRIGGER_LABEL,
    triggerAriaLabel = "",
    highlightToolText = HIGHLIGHT_TOOL_TEXT,
    hideToolText = HIDE_TOOL_TEXT,
    removeHighlightText = REMOVE_HIGHLIGHT_TEXT,
    errorEmptyMessageText = ERROR_EMPTY_MESSAGE_TEXT,
    errorNoClientText = ERROR_NO_CLIENT_TEXT,
    errorTimeoutText = ERROR_TIMEOUT_TEXT,
    errorForbiddenText = ERROR_FORBIDDEN_TEXT,
    errorGenericText = ERROR_GENERIC_TEXT,
    // FeedbackCallbacks
    onFormOpen,
    onFormClose,
    onSubmitSuccess,
    onSubmitError,
    onFormSubmitted
  } = {}) => {
    const _options = {
      id,
      autoInject,
      showBranding,
      isEmailRequired,
      isNameRequired,
      showEmail,
      showName,
      enableScreenshot,
      useSentryUser,
      tags,
      styleNonce,
      scriptNonce,
      colorScheme,
      themeDark,
      themeLight,
      triggerLabel,
      triggerAriaLabel,
      cancelButtonLabel,
      submitButtonLabel,
      confirmButtonLabel,
      formTitle,
      emailLabel,
      emailPlaceholder,
      messageLabel,
      messagePlaceholder,
      nameLabel,
      namePlaceholder,
      successMessageText,
      isRequiredLabel,
      addScreenshotButtonLabel,
      removeScreenshotButtonLabel,
      highlightToolText,
      hideToolText,
      removeHighlightText,
      errorEmptyMessageText,
      errorNoClientText,
      errorTimeoutText,
      errorForbiddenText,
      errorGenericText,
      onFormClose,
      onFormOpen,
      onSubmitError,
      onSubmitSuccess,
      onFormSubmitted
    };
    let _shadow = null;
    let _mainStyle = null;
    let _subscriptions = [];
    const _createShadow = (options) => {
      if (!_shadow) {
        const host = DOCUMENT.createElement("div");
        host.id = String(options.id);
        DOCUMENT.body.appendChild(host);
        _shadow = host.attachShadow({ mode: "open" });
        _mainStyle = createMainStyles(options);
        _shadow.appendChild(_mainStyle);
      }
      return _shadow;
    };
    const _loadAndRenderDialog = async (options) => {
      const screenshotRequired = options.enableScreenshot && isScreenshotSupported();
      let modalIntegration;
      let screenshotIntegration;
      try {
        const modalIntegrationFn = getModalIntegration ? getModalIntegration() : await lazyLoadIntegration("feedbackModalIntegration", scriptNonce);
        modalIntegration = modalIntegrationFn();
        addIntegration(modalIntegration);
      } catch {
        DEBUG_BUILD && debug.error(
          "[Feedback] Error when trying to load feedback integrations. Try using `feedbackSyncIntegration` in your `Sentry.init`."
        );
        throw new Error("[Feedback] Missing feedback modal integration!");
      }
      try {
        const screenshotIntegrationFn = screenshotRequired ? getScreenshotIntegration ? getScreenshotIntegration() : await lazyLoadIntegration("feedbackScreenshotIntegration", scriptNonce) : void 0;
        if (screenshotIntegrationFn) {
          screenshotIntegration = screenshotIntegrationFn();
          addIntegration(screenshotIntegration);
        }
      } catch {
        DEBUG_BUILD && debug.error("[Feedback] Missing feedback screenshot integration. Proceeding without screenshots.");
      }
      const errorMessages = {
        ERROR_EMPTY_MESSAGE: options.errorEmptyMessageText,
        ERROR_NO_CLIENT: options.errorNoClientText,
        ERROR_TIMEOUT: options.errorTimeoutText,
        ERROR_FORBIDDEN: options.errorForbiddenText,
        ERROR_GENERIC: options.errorGenericText
      };
      const wrappedSendFeedback = (params, hint) => sendFeedback(params, { includeReplay: true, ...hint, errorMessages });
      const dialog = modalIntegration.createDialog({
        options: {
          ...options,
          onFormClose: () => {
            dialog?.close();
            options.onFormClose?.();
          },
          onFormSubmitted: () => {
            dialog?.close();
            options.onFormSubmitted?.();
          }
        },
        screenshotIntegration,
        sendFeedback: wrappedSendFeedback,
        shadow: _createShadow(options)
      });
      return dialog;
    };
    const _attachTo = (el, optionOverrides = {}) => {
      const mergedOptions = mergeOptions(_options, optionOverrides);
      const targetEl = typeof el === "string" ? DOCUMENT.querySelector(el) : typeof el.addEventListener === "function" ? el : null;
      if (!targetEl) {
        DEBUG_BUILD && debug.error("[Feedback] Unable to attach to target element");
        throw new Error("Unable to attach to target element");
      }
      let dialog = null;
      const handleClick = async () => {
        if (!dialog) {
          dialog = await _loadAndRenderDialog({
            ...mergedOptions,
            onFormSubmitted: () => {
              dialog?.removeFromDom();
              mergedOptions.onFormSubmitted?.();
            }
          });
        }
        dialog.appendToDom();
        dialog.open();
      };
      targetEl.addEventListener("click", handleClick);
      const unsubscribe = () => {
        _subscriptions = _subscriptions.filter((sub) => sub !== unsubscribe);
        dialog?.removeFromDom();
        dialog = null;
        targetEl.removeEventListener("click", handleClick);
      };
      _subscriptions.push(unsubscribe);
      return unsubscribe;
    };
    const _createActor = (optionOverrides = {}) => {
      const mergedOptions = mergeOptions(_options, optionOverrides);
      const shadow = _createShadow(mergedOptions);
      const actor = Actor({
        triggerLabel: mergedOptions.triggerLabel,
        triggerAriaLabel: mergedOptions.triggerAriaLabel,
        shadow,
        styleNonce
      });
      _attachTo(actor.el, {
        ...mergedOptions,
        onFormOpen() {
          actor.hide();
        },
        onFormClose() {
          actor.show();
        },
        onFormSubmitted() {
          actor.show();
        }
      });
      return actor;
    };
    return {
      name: "Feedback",
      setupOnce() {
        if (!isBrowser() || !_options.autoInject) {
          return;
        }
        if (DOCUMENT.readyState === "loading") {
          DOCUMENT.addEventListener("DOMContentLoaded", () => _createActor().appendToDom());
        } else {
          _createActor().appendToDom();
        }
      },
      /**
       * Adds click listener to the element to open a feedback dialog
       *
       * The returned function can be used to remove the click listener
       */
      attachTo: _attachTo,
      /**
       * Creates a new widget which is composed of a Button which triggers a Dialog.
       * Accepts partial options to override any options passed to constructor.
       */
      createWidget(optionOverrides = {}) {
        const actor = _createActor(mergeOptions(_options, optionOverrides));
        actor.appendToDom();
        return actor;
      },
      /**
       * Creates a new Form which you can
       * Accepts partial options to override any options passed to constructor.
       */
      async createForm(optionOverrides = {}) {
        return _loadAndRenderDialog(mergeOptions(_options, optionOverrides));
      },
      /**
       * Updates the color scheme of the feedback widget at runtime.
       */
      setTheme(colorScheme2) {
        _options.colorScheme = colorScheme2;
        if (_shadow) {
          const newStyle = createMainStyles(_options);
          if (_mainStyle) {
            _shadow.replaceChild(newStyle, _mainStyle);
          } else {
            _shadow.prepend(newStyle);
          }
          _mainStyle = newStyle;
        }
      },
      /**
       * Removes the Feedback integration (including host, shadow DOM, and all widgets)
       */
      remove() {
        if (_shadow) {
          _shadow.parentElement?.remove();
          _shadow = null;
          _mainStyle = null;
        }
        _subscriptions.forEach((sub) => sub());
        _subscriptions = [];
      }
    };
  });
  return feedbackIntegration;
};

function getFeedback() {
  const client = getClient();
  return client?.getIntegrationByName("Feedback");
}

var n,l$1,u$1,i$1,r$1,o$1,e$1,f$1,c$1,a$1,s$1,h$1,p$1,v$1,d$1={},w$1=[],_$1=/acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i,g$1=Array.isArray;function m$1(n,l){for(var u in l)n[u]=l[u];return n}function b$1(n){n&&n.parentNode&&n.parentNode.removeChild(n);}function k$1(l,u,t){var i,r,o,e={};for(o in u)"key"==o?i=u[o]:"ref"==o?r=u[o]:e[o]=u[o];if(arguments.length>2&&(e.children=arguments.length>3?n.call(arguments,2):t),"function"==typeof l&&null!=l.defaultProps)for(o in l.defaultProps) void 0===e[o]&&(e[o]=l.defaultProps[o]);return x$1(l,e,i,r,null)}function x$1(n,t,i,r,o){var e={type:n,props:t,key:i,ref:r,__k:null,__:null,__b:0,__e:null,__c:null,constructor:void 0,__v:null==o?++u$1:o,__i:-1,__u:0};return null==o&&null!=l$1.vnode&&l$1.vnode(e),e}function S(n){return n.children}function C$1(n,l){this.props=n,this.context=l;}function $(n,l){if(null==l)return n.__?$(n.__,n.__i+1):null;for(var u;l<n.__k.length;l++)if(null!=(u=n.__k[l])&&null!=u.__e)return u.__e;return "function"==typeof n.type?$(n):null}function I(n){if(n.__P&&n.__d){var u=n.__v,t=u.__e,i=[],r=[],o=m$1({},u);o.__v=u.__v+1,l$1.vnode&&l$1.vnode(o),q$1(n.__P,o,u,n.__n,n.__P.namespaceURI,32&u.__u?[t]:null,i,null==t?$(u):t,!!(32&u.__u),r),o.__v=u.__v,o.__.__k[o.__i]=o,D$1(i,o,r),u.__e=u.__=null,o.__e!=t&&P$1(o);}}function P$1(n){if(null!=(n=n.__)&&null!=n.__c)return n.__e=n.__c.base=null,n.__k.some(function(l){if(null!=l&&null!=l.__e)return n.__e=n.__c.base=l.__e}),P$1(n)}function A$1(n){(!n.__d&&(n.__d=true)&&i$1.push(n)&&!H.__r++||r$1!=l$1.debounceRendering)&&((r$1=l$1.debounceRendering)||o$1)(H);}function H(){try{for(var n,l=1;i$1.length;)i$1.length>l&&i$1.sort(e$1),n=i$1.shift(),l=i$1.length,I(n);}finally{i$1.length=H.__r=0;}}function L(n,l,u,t,i,r,o,e,f,c,a){var s,h,p,v,y,_,g=t&&t.__k||w$1,m=l.length;for(f=T$1(u,l,g,f,m),s=0;s<m;s++)null!=(p=u.__k[s])&&(h=-1!=p.__i&&g[p.__i]||d$1,p.__i=s,_=q$1(n,p,h,i,r,o,e,f,c,a),v=p.__e,p.ref&&h.ref!=p.ref&&(h.ref&&J(h.ref,null,p),a.push(p.ref,p.__c||v,p)),null==y&&null!=v&&(y=v),4&p.__u?(f=j$1(p,f,n),h.__e&&(h.__e=null)):"function"==typeof p.type&&void 0!==_?f=_:v&&(f=v.nextSibling),p.__u&=-7);return u.__e=y,f}function T$1(n,l,u,t,i){var r,o,e,f,c,a=u.length,s=a,h=0;for(n.__k=new Array(i),r=0;r<i;r++)null!=(o=l[r])&&"boolean"!=typeof o&&"function"!=typeof o?("string"==typeof o||"number"==typeof o||"bigint"==typeof o||o.constructor==String?o=n.__k[r]=x$1(null,o,null,null,null):g$1(o)?o=n.__k[r]=x$1(S,{children:o},null,null,null):void 0===o.constructor&&o.__b>0?o=n.__k[r]=x$1(o.type,o.props,o.key,o.ref?o.ref:null,o.__v):n.__k[r]=o,f=r+h,o.__=n,o.__b=n.__b+1,e=null,-1!=(c=o.__i=O(o,u,f,s))&&(s--,(e=u[c])&&(e.__u|=2)),null==e||null==e.__v?(-1==c&&(i>a?h--:i<a&&h++),"function"!=typeof o.type&&(o.__u|=4)):c!=f&&(c==f-1?h--:c==f+1?h++:(c>f?h--:h++,o.__u|=4))):n.__k[r]=null;if(s)for(r=0;r<a;r++)null!=(e=u[r])&&0==(2&e.__u)&&(e.__e==t&&(t=$(e)),K(e,e));return t}function j$1(n,l,u){var t,i;if("function"==typeof n.type){for(t=n.__k,i=0;t&&i<t.length;i++)t[i]&&(t[i].__=n,l=j$1(t[i],l,u));return l}n.__e!=l&&(l&&n.type&&!l.parentNode&&(l=$(n)),l=u.insertBefore(n.__e,l||null));do{l=l&&l.nextSibling;}while(null!=l&&8==l.nodeType);return l}function O(n,l,u,t){var i,r,o,e=n.key,f=n.type,c=l[u],a=null!=c&&0==(2&c.__u);if(null===c&&null==e||a&&e==c.key&&f==c.type)return u;if(t>(a?1:0))for(i=u-1,r=u+1;i>=0||r<l.length;)if(null!=(c=l[o=i>=0?i--:r++])&&0==(2&c.__u)&&e==c.key&&f==c.type)return o;return  -1}function z$1(n,l,u){"-"==l[0]?n.setProperty(l,null==u?"":u):n[l]=null==u?"":"number"!=typeof u||_$1.test(l)?u:u+"px";}function N(n,l,u,t,i){var r,o;n:if("style"==l)if("string"==typeof u)n.style.cssText=u;else {if("string"==typeof t&&(n.style.cssText=t=""),t)for(l in t)u&&l in u||z$1(n.style,l,"");if(u)for(l in u)t&&u[l]==t[l]||z$1(n.style,l,u[l]);}else if("o"==l[0]&&"n"==l[1])r=l!=(l=l.replace(s$1,"$1")),o=l.toLowerCase(),l=o in n||"onFocusOut"==l||"onFocusIn"==l?o.slice(2):l.slice(2),n.l||(n.l={}),n.l[l+r]=u,u?t?u[a$1]=t[a$1]:(u[a$1]=h$1,n.addEventListener(l,r?v$1:p$1,r)):n.removeEventListener(l,r?v$1:p$1,r);else {if("http://www.w3.org/2000/svg"==i)l=l.replace(/xlink(H|:h)/,"h").replace(/sName$/,"s");else if("width"!=l&&"height"!=l&&"href"!=l&&"list"!=l&&"form"!=l&&"tabIndex"!=l&&"download"!=l&&"rowSpan"!=l&&"colSpan"!=l&&"role"!=l&&"popover"!=l&&l in n)try{n[l]=null==u?"":u;break n}catch(n){}"function"==typeof u||(null==u||false===u&&"-"!=l[4]?n.removeAttribute(l):n.setAttribute(l,"popover"==l&&1==u?"":u));}}function V(n){return function(u){if(this.l){var t=this.l[u.type+n];if(null==u[c$1])u[c$1]=h$1++;else if(u[c$1]<t[a$1])return;return t(l$1.event?l$1.event(u):u)}}}function q$1(n,u,t,i,r,o,e,f,c,a){var s,h,p,v,y,d,_,k,x,M,I,P,A,H,T,j,F=u.type;if(void 0!==u.constructor)return null;128&t.__u&&(c=!!(32&t.__u),o=[f=u.__e=t.__e]),(s=l$1.__b)&&s(u);n:if("function"==typeof F){h=e.length;try{if(x=u.props,M=F.prototype&&F.prototype.render,I=(s=F.contextType)&&i[s.__c],P=s?I?I.props.value:s.__:i,t.__c?k=(p=u.__c=t.__c).__=p.__E:(M?u.__c=p=new F(x,P):(u.__c=p=new C$1(x,P),p.constructor=F,p.render=Q),I&&I.sub(p),p.state||(p.state={}),p.__n=i,v=p.__d=!0,p.__h=[],p._sb=[]),M&&null==p.__s&&(p.__s=p.state),M&&null!=F.getDerivedStateFromProps&&(p.__s==p.state&&(p.__s=m$1({},p.__s)),m$1(p.__s,F.getDerivedStateFromProps(x,p.__s))),y=p.props,d=p.state,p.__v=u,v)M&&null==F.getDerivedStateFromProps&&null!=p.componentWillMount&&p.componentWillMount(),M&&null!=p.componentDidMount&&p.__h.push(p.componentDidMount);else {if(M&&null==F.getDerivedStateFromProps&&x!==y&&null!=p.componentWillReceiveProps&&p.componentWillReceiveProps(x,P),u.__v==t.__v||!p.__e&&null!=p.shouldComponentUpdate&&!1===p.shouldComponentUpdate(x,p.__s,P)){u.__v!=t.__v&&(p.props=x,p.state=p.__s,p.__d=!1),u.__e=t.__e,u.__k=t.__k,u.__k.some(function(n){n&&(n.__=u);}),w$1.push.apply(p.__h,p._sb),p._sb=[],p.__h.length&&e.push(p),f=$(t);break n}null!=p.componentWillUpdate&&p.componentWillUpdate(x,p.__s,P),M&&null!=p.componentDidUpdate&&p.__h.push(function(){p.componentDidUpdate(y,d,_);});}if(p.context=P,p.props=x,p.__P=n,p.__e=!1,A=l$1.__r,H=0,M)p.state=p.__s,p.__d=!1,A&&A(u),s=p.render(p.props,p.state,p.context),w$1.push.apply(p.__h,p._sb),p._sb=[];else do{p.__d=!1,A&&A(u),s=p.render(p.props,p.state,p.context),p.state=p.__s;}while(p.__d&&++H<25);p.state=p.__s,null!=p.getChildContext&&(i=m$1(m$1({},i),p.getChildContext())),M&&!v&&null!=p.getSnapshotBeforeUpdate&&(_=p.getSnapshotBeforeUpdate(y,d)),T=null!=s&&s.type===S&&null==s.key?E(s.props.children):s,f=L(n,g$1(T)?T:[T],u,t,i,r,o,e,f,c,a),p.base=u.__e,u.__u&=-161,p.__h.length&&e.push(p),k&&(p.__E=p.__=null);}catch(n){if(e.length=h,u.__v=null,c||null!=o){if(n.then){for(u.__u|=c?160:128;f&&8==f.nodeType&&f.nextSibling;)f=f.nextSibling;null!=o&&(o[o.indexOf(f)]=null),u.__e=f;}else if(null!=o)for(j=o.length;j--;)b$1(o[j]);}else u.__e=t.__e;null==u.__k&&(u.__k=t.__k||[]),n.then||B$1(u),l$1.__e(n,u,t);}}else null==o&&u.__v==t.__v?(u.__k=t.__k,u.__e=t.__e):f=u.__e=G(t.__e,u,t,i,r,o,e,c,a);return (s=l$1.diffed)&&s(u),128&u.__u?void 0:f}function B$1(n){n&&(n.__c&&(n.__c.__e=true),n.__k&&n.__k.some(B$1));}function D$1(n,u,t){for(var i=0;i<t.length;i++)J(t[i],t[++i],t[++i]);l$1.__c&&l$1.__c(u,n),n.some(function(u){try{n=u.__h,u.__h=[],n.some(function(n){n.call(u);});}catch(n){l$1.__e(n,u.__v);}});}function E(n){return "object"!=typeof n||null==n||n.__b>0?n:g$1(n)?n.map(E):void 0!==n.constructor?null:m$1({},n)}function G(u,t,i,r,o,e,f,c,a){var s,h,p,v,y,w,_,m=i.props||d$1,k=t.props,x=t.type;if("svg"==x?o="http://www.w3.org/2000/svg":"math"==x?o="http://www.w3.org/1998/Math/MathML":o||(o="http://www.w3.org/1999/xhtml"),null!=e)for(s=0;s<e.length;s++)if((y=e[s])&&"setAttribute"in y==!!x&&(x?y.localName==x:3==y.nodeType)){u=y,e[s]=null;break}if(null==u){if(null==x)return document.createTextNode(k);u=document.createElementNS(o,x,k.is&&k),c&&(l$1.__m&&l$1.__m(t,e),c=false),e=null;}if(null==x)m===k||c&&u.data==k||(u.data=k);else {if(e="textarea"==x&&null!=k.defaultValue?null:e&&n.call(u.childNodes),!c&&null!=e)for(m={},s=0;s<u.attributes.length;s++)m[(y=u.attributes[s]).name]=y.value;for(s in m)y=m[s],"dangerouslySetInnerHTML"==s?p=y:"children"==s||s in k||"value"==s&&"defaultValue"in k||"checked"==s&&"defaultChecked"in k||N(u,s,null,y,o);for(s in k)y=k[s],"children"==s?v=y:"dangerouslySetInnerHTML"==s?h=y:"value"==s?w=y:"checked"==s?_=y:c&&"function"!=typeof y||m[s]===y||N(u,s,y,m[s],o);if(h)c||p&&(h.__html==p.__html||h.__html==u.innerHTML)||(u.innerHTML=h.__html),t.__k=[];else if(p&&(u.innerHTML=""),L("template"==t.type?u.content:u,g$1(v)?v:[v],t,i,r,"foreignObject"==x?"http://www.w3.org/1999/xhtml":o,e,f,e?e[0]:i.__k&&$(i,0),c,a),null!=e)for(s=e.length;s--;)b$1(e[s]);c&&"textarea"!=x||(s="value","progress"==x&&null==w?u.removeAttribute("value"):null!=w&&(w!==u[s]||"progress"==x&&!w||"option"==x&&w!=m[s])&&N(u,s,w,m[s],o),s="checked",null!=_&&_!=u[s]&&N(u,s,_,m[s],o));}return u}function J(n,u,t){try{if("function"==typeof n){var i="function"==typeof n.__u;i&&n.__u(),i&&null==u||(n.__u=n(u));}else n.current=u;}catch(n){l$1.__e(n,t);}}function K(n,u,t){var i,r;if(l$1.unmount&&l$1.unmount(n),(i=n.ref)&&(i.current&&i.current!=n.__e||J(i,null,u)),null!=(i=n.__c)){if(i.componentWillUnmount)try{i.componentWillUnmount();}catch(n){l$1.__e(n,u);}i.base=i.__P=i.__n=null;}if(i=n.__k)for(r=0;r<i.length;r++)i[r]&&K(i[r],u,t||"function"!=typeof n.type);t||b$1(n.__e),n.__c=n.__=n.__e=void 0;}function Q(n,l,u){return this.constructor(n,u)}function R(u,t,i){var r,o,e,f;t==document&&(t=document.documentElement),l$1.__&&l$1.__(u,t),o=(r="function"=="undefined")?null:t.__k,e=[],f=[],q$1(t,u=(t).__k=k$1(S,null,[u]),o||d$1,d$1,t.namespaceURI,o?null:t.firstChild?n.call(t.childNodes):null,e,o?o.__e:t.firstChild,r,f),D$1(e,u,f),u.props.children=null;}n=w$1.slice,l$1={__e:function(n,l,u,t){for(var i,r,o;l=l.__;)if((i=l.__c)&&!i.__)try{if((r=i.constructor)&&null!=r.getDerivedStateFromError&&(i.setState(r.getDerivedStateFromError(n)),o=i.__d),null!=i.componentDidCatch&&(i.componentDidCatch(n,t||{}),o=i.__d),o)return i.__E=i}catch(l){n=l;}throw n}},u$1=0,C$1.prototype.setState=function(n,l){var u;u=null!=this.__s&&this.__s!=this.state?this.__s:this.__s=m$1({},this.state),"function"==typeof n&&(n=n(m$1({},u),this.props)),n&&m$1(u,n),null!=n&&this.__v&&(l&&this._sb.push(l),A$1(this));},C$1.prototype.forceUpdate=function(n){this.__v&&(this.__e=true,n&&this.__h.push(n),A$1(this));},C$1.prototype.render=S,i$1=[],o$1="function"==typeof Promise?Promise.prototype.then.bind(Promise.resolve()):setTimeout,e$1=function(n,l){return n.__v.__b-l.__v.__b},H.__r=0,f$1=Math.random().toString(8),c$1="__d"+f$1,a$1="__a"+f$1,s$1=/(PointerCapture)$|Capture$/i,h$1=0,p$1=V(false),v$1=V(true);

var t,r,u,i,o=0,f=[],c=l$1,e=c.__b,a=c.__r,v=c.diffed,l=c.__c,m=c.unmount,p=c.__;function s(n,t){c.__h&&c.__h(r,n,o||t),o=0;var u=r.__H||(r.__H={__:[],__h:[]});return n>=u.__.length&&u.__.push({}),u.__[n]}function d(n){return o=1,y(D,n)}function y(n,u,i){var o=s(t++,2);if(o.t=n,!o.__c&&(o.__=[i?i(u):D(void 0,u),function(n){var t=o.__N?o.__N[0]:o.__[0],r=o.t(t,n);t!==r&&(o.__N=[r,o.__[1]],o.__c.setState({}));}],o.__c=r,!r.__f)){var f=function(n,t,r){if(!o.__c.__H)return  true;var u=false,i=o.__c.props!==n;if(o.__c.__H.__.some(function(n){if(n.__N){u=true;var t=n.__[0];n.__=n.__N,n.__N=void 0,t!==n.__[0]&&(i=true);}}),c){var f=c.call(this,n,t,r);return u?f||i:f}return !u||i};r.__f=true;var c=r.shouldComponentUpdate,e=r.componentWillUpdate;r.componentWillUpdate=function(n,t,r){if(this.__e){var u=c;c=void 0,f(n,t,r),c=u;}e&&e.call(this,n,t,r);},r.shouldComponentUpdate=f;}return o.__N||o.__}function h(n,u){var i=s(t++,3);!c.__s&&C(i.__H,u)&&(i.__=n,i.u=u,r.__H.__h.push(i));}function _(n,u){var i=s(t++,4);!c.__s&&C(i.__H,u)&&(i.__=n,i.u=u,r.__h.push(i));}function A(n){return o=5,T(function(){return {current:n}},[])}function F(n,t,r){o=6,_(function(){if("function"==typeof n){var r=n(t());return function(){n(null),r&&"function"==typeof r&&r();}}if(n)return n.current=t(),function(){return n.current=null}},null==r?r:r.concat(n));}function T(n,r){var u=s(t++,7);return C(u.__H,r)&&(u.__=n(),u.__H=r,u.__h=n),u.__}function q(n,t){return o=8,T(function(){return n},t)}function x(n){var u=r.context[n.__c],i=s(t++,9);return i.c=n,u?(null==i.__&&(i.__=true,u.sub(r)),u.props.value):n.__}function P(n,t){c.useDebugValue&&c.useDebugValue(t?t(n):n);}function b(n){var u=s(t++,10),i=d();return u.__=n,r.componentDidCatch||(r.componentDidCatch=function(n,t){u.__&&u.__(n,t),i[1](n);}),[i[0],function(){i[1](void 0);}]}function g(){var n=s(t++,11);if(!n.__){for(var u=r.__v;null!==u&&!u.__m&&null!==u.__;)u=u.__;var i=u.__m||(u.__m=[0,0]);n.__="P"+i[0]+"-"+i[1]++;}return n.__}function j(){for(var n;n=f.shift();){var t=n.__H;if(n.__P&&t)try{t.__h.some(z),t.__h.some(B),t.__h=[];}catch(r){t.__h=[],c.__e(r,n.__v);}}}c.__b=function(n){r=null,e&&e(n);},c.__=function(n,t){n&&t.__k&&t.__k.__m&&(n.__m=t.__k.__m),p&&p(n,t);},c.__r=function(n){a&&a(n),t=0;var i=(r=n.__c).__H;i&&(u===r?(i.__h=[],r.__h=[],i.__.some(function(n){n.__N&&(n.__=n.__N),n.u=n.__N=void 0;})):(i.__h.some(z),i.__h.some(B),i.__h=[],t=0)),u=r;},c.diffed=function(n){v&&v(n);var t=n.__c;t&&t.__H&&(t.__H.__h.length&&(1!==f.push(t)&&i===c.requestAnimationFrame||((i=c.requestAnimationFrame)||w)(j)),t.__H.__.some(function(n){n.u&&(n.__H=n.u,n.u=void 0);})),u=r=null;},c.__c=function(n,t){t.some(function(n){try{n.__h.some(z),n.__h=n.__h.filter(function(n){return !n.__||B(n)});}catch(r){t.some(function(n){n.__h&&(n.__h=[]);}),t=[],c.__e(r,n.__v);}}),l&&l(n,t);},c.unmount=function(n){m&&m(n);var t,r=n.__c;r&&r.__H&&(r.__H.__.some(function(n){try{z(n);}catch(n){t=n;}}),r.__H=void 0,t&&c.__e(t,r.__v));};var k="function"==typeof requestAnimationFrame;function w(n){var t,r=function(){clearTimeout(u),k&&cancelAnimationFrame(t),setTimeout(n);},u=setTimeout(r,35);k&&(t=requestAnimationFrame(r));}function z(n){var t=r,u=n.__c;"function"==typeof u&&(n.__c=void 0,u()),r=t;}function B(n){var t=r;n.__c=n.__(),r=t;}function C(n,t){return !n||n.length!==t.length||t.some(function(t,r){return t!==n[r]})}function D(n,t){return "function"==typeof t?t(n):t}

const hooks = /*#__PURE__*/Object.defineProperty({
  __proto__: null,
  useCallback: q,
  useContext: x,
  useDebugValue: P,
  useEffect: h,
  useErrorBoundary: b,
  useId: g,
  useImperativeHandle: F,
  useLayoutEffect: _,
  useMemo: T,
  useReducer: y,
  useRef: A,
  useState: d
}, Symbol.toStringTag, { value: 'Module' });

const XMLNS$1 = "http://www.w3.org/2000/svg";
function SentryLogo() {
  const createElementNS = (tagName) => DOCUMENT.createElementNS(XMLNS$1, tagName);
  const svg = setAttributesNS(createElementNS("svg"), {
    width: "32",
    height: "30",
    viewBox: "0 0 72 66",
    fill: "inherit"
  });
  const path = setAttributesNS(createElementNS("path"), {
    transform: "translate(11, 11)",
    d: "M29,2.26a4.67,4.67,0,0,0-8,0L14.42,13.53A32.21,32.21,0,0,1,32.17,40.19H27.55A27.68,27.68,0,0,0,12.09,17.47L6,28a15.92,15.92,0,0,1,9.23,12.17H4.62A.76.76,0,0,1,4,39.06l2.94-5a10.74,10.74,0,0,0-3.36-1.9l-2.91,5a4.54,4.54,0,0,0,1.69,6.24A4.66,4.66,0,0,0,4.62,44H19.15a19.4,19.4,0,0,0-8-17.31l2.31-4A23.87,23.87,0,0,1,23.76,44H36.07a35.88,35.88,0,0,0-16.41-31.8l4.67-8a.77.77,0,0,1,1.05-.27c.53.29,20.29,34.77,20.66,35.17a.76.76,0,0,1-.68,1.13H40.6q.09,1.91,0,3.81h4.78A4.59,4.59,0,0,0,50,39.43a4.49,4.49,0,0,0-.62-2.28Z"
  });
  svg.appendChild(path);
  return svg;
}

function DialogHeader({ options }) {
  const logoHtml = T(() => ({ __html: SentryLogo().outerHTML }), []);
  return /* @__PURE__ */ k$1("h2", { class: "dialog__header" }, /* @__PURE__ */ k$1("span", { class: "dialog__title" }, options.formTitle), options.showBranding ? /* @__PURE__ */ k$1(
    "a",
    {
      class: "brand-link",
      target: "_blank",
      href: "https://sentry.io/welcome/",
      title: "Powered by Sentry",
      rel: "noopener noreferrer",
      dangerouslySetInnerHTML: logoHtml
    }
  ) : null);
}

function getMissingFields(feedback, props) {
  const emptyFields = [];
  if (props.isNameRequired && !feedback.name) {
    emptyFields.push(props.nameLabel);
  }
  if (props.isEmailRequired && !feedback.email) {
    emptyFields.push(props.emailLabel);
  }
  if (!feedback.message) {
    emptyFields.push(props.messageLabel);
  }
  return emptyFields;
}

function retrieveStringValue(formData, key) {
  const value = formData.get(key);
  if (typeof value === "string") {
    return value.trim();
  }
  return "";
}
function Form({
  options,
  defaultEmail,
  defaultName,
  onFormClose,
  onSubmit,
  onSubmitSuccess,
  onSubmitError,
  showEmail,
  showName,
  screenshotInput
}) {
  const {
    tags,
    addScreenshotButtonLabel,
    removeScreenshotButtonLabel,
    cancelButtonLabel,
    emailLabel,
    emailPlaceholder,
    isEmailRequired,
    isNameRequired,
    messageLabel,
    messagePlaceholder,
    nameLabel,
    namePlaceholder,
    submitButtonLabel,
    isRequiredLabel
  } = options;
  const [isSubmitting, setIsSubmitting] = d(false);
  const [error, setError] = d(null);
  const [showScreenshotInput, setShowScreenshotInput] = d(false);
  const ScreenshotInputComponent = screenshotInput?.input;
  const [screenshotError, setScreenshotError] = d(null);
  const onScreenshotError = q((error2) => {
    setScreenshotError(error2);
    setShowScreenshotInput(false);
  }, []);
  const hasAllRequiredFields = q(
    (data) => {
      const missingFields = getMissingFields(data, {
        emailLabel,
        isEmailRequired,
        isNameRequired,
        messageLabel,
        nameLabel
      });
      if (missingFields.length > 0) {
        setError(`Please enter in the following required fields: ${missingFields.join(", ")}`);
      } else {
        setError(null);
      }
      return missingFields.length === 0;
    },
    [emailLabel, isEmailRequired, isNameRequired, messageLabel, nameLabel]
  );
  const handleSubmit = q(
    async (e) => {
      setIsSubmitting(true);
      try {
        e.preventDefault();
        if (!(e.target instanceof HTMLFormElement)) {
          return;
        }
        const formData = new FormData(e.target);
        const attachment = await (screenshotInput && showScreenshotInput ? screenshotInput.value() : void 0);
        const data = {
          name: retrieveStringValue(formData, "name"),
          email: retrieveStringValue(formData, "email"),
          message: retrieveStringValue(formData, "message"),
          attachments: attachment ? [attachment] : void 0
        };
        if (!hasAllRequiredFields(data)) {
          return;
        }
        try {
          const eventId = await onSubmit(
            {
              name: data.name,
              email: data.email,
              message: data.message,
              source: FEEDBACK_WIDGET_SOURCE,
              tags
            },
            { attachments: data.attachments }
          );
          onSubmitSuccess(data, eventId);
        } catch (error2) {
          DEBUG_BUILD && debug.error(error2);
          const err = error2;
          setError(err.message);
          onSubmitError(err);
        }
      } finally {
        setIsSubmitting(false);
      }
    },
    [screenshotInput && showScreenshotInput, onSubmitSuccess, onSubmitError]
  );
  return /* @__PURE__ */ k$1("form", { class: "form", onSubmit: handleSubmit }, ScreenshotInputComponent && showScreenshotInput ? /* @__PURE__ */ k$1(ScreenshotInputComponent, { onError: onScreenshotError }) : null, /* @__PURE__ */ k$1("fieldset", { class: "form__right", "data-sentry-feedback": true, disabled: isSubmitting }, /* @__PURE__ */ k$1("div", { class: "form__top" }, error ? /* @__PURE__ */ k$1("div", { class: "form__error-container" }, error) : null, showName ? /* @__PURE__ */ k$1("label", { for: "name", class: "form__label" }, /* @__PURE__ */ k$1(LabelText, { label: nameLabel, isRequiredLabel, isRequired: isNameRequired }), /* @__PURE__ */ k$1(
    "input",
    {
      class: "form__input",
      defaultValue: defaultName,
      id: "name",
      name: "name",
      placeholder: namePlaceholder,
      required: isNameRequired,
      type: "text"
    }
  )) : /* @__PURE__ */ k$1("input", { "aria-hidden": true, value: defaultName, name: "name", type: "hidden" }), showEmail ? /* @__PURE__ */ k$1("label", { for: "email", class: "form__label" }, /* @__PURE__ */ k$1(LabelText, { label: emailLabel, isRequiredLabel, isRequired: isEmailRequired }), /* @__PURE__ */ k$1(
    "input",
    {
      class: "form__input",
      defaultValue: defaultEmail,
      id: "email",
      name: "email",
      placeholder: emailPlaceholder,
      required: isEmailRequired,
      type: "email"
    }
  )) : /* @__PURE__ */ k$1("input", { "aria-hidden": true, value: defaultEmail, name: "email", type: "hidden" }), /* @__PURE__ */ k$1("label", { for: "message", class: "form__label" }, /* @__PURE__ */ k$1(LabelText, { label: messageLabel, isRequiredLabel, isRequired: true }), /* @__PURE__ */ k$1(
    "textarea",
    {
      autoFocus: true,
      class: "form__input form__input--textarea",
      id: "message",
      name: "message",
      placeholder: messagePlaceholder,
      required: true,
      rows: 5
    }
  )), ScreenshotInputComponent ? /* @__PURE__ */ k$1("label", { for: "screenshot", class: "form__label" }, /* @__PURE__ */ k$1(
    "button",
    {
      class: "btn btn--default",
      disabled: isSubmitting,
      type: "button",
      onClick: () => {
        setScreenshotError(null);
        setShowScreenshotInput((prev) => !prev);
      }
    },
    showScreenshotInput ? removeScreenshotButtonLabel : addScreenshotButtonLabel
  ), screenshotError ? /* @__PURE__ */ k$1("div", { class: "form__error-container" }, screenshotError.message) : null) : null), /* @__PURE__ */ k$1("div", { class: "btn-group" }, /* @__PURE__ */ k$1("button", { class: "btn btn--primary", disabled: isSubmitting, type: "submit" }, submitButtonLabel), /* @__PURE__ */ k$1("button", { class: "btn btn--default", disabled: isSubmitting, type: "button", onClick: onFormClose }, cancelButtonLabel))));
}
function LabelText({
  label,
  isRequired,
  isRequiredLabel
}) {
  return /* @__PURE__ */ k$1("span", { class: "form__label__text" }, label, isRequired && /* @__PURE__ */ k$1("span", { class: "form__label__text--required" }, isRequiredLabel));
}

const WIDTH = 16;
const HEIGHT = 17;
const XMLNS = "http://www.w3.org/2000/svg";
function SuccessIcon() {
  const createElementNS = (tagName) => WINDOW.document.createElementNS(XMLNS, tagName);
  const svg = setAttributesNS(createElementNS("svg"), {
    width: `${WIDTH}`,
    height: `${HEIGHT}`,
    viewBox: `0 0 ${WIDTH} ${HEIGHT}`,
    fill: "inherit"
  });
  const g = setAttributesNS(createElementNS("g"), {
    clipPath: "url(#clip0_57_156)"
  });
  const path2 = setAttributesNS(createElementNS("path"), {
    ["fill-rule"]: "evenodd",
    ["clip-rule"]: "evenodd",
    d: "M3.55544 15.1518C4.87103 16.0308 6.41775 16.5 8 16.5C10.1217 16.5 12.1566 15.6571 13.6569 14.1569C15.1571 12.6566 16 10.6217 16 8.5C16 6.91775 15.5308 5.37103 14.6518 4.05544C13.7727 2.73985 12.5233 1.71447 11.0615 1.10897C9.59966 0.503466 7.99113 0.34504 6.43928 0.653721C4.88743 0.962403 3.46197 1.72433 2.34315 2.84315C1.22433 3.96197 0.462403 5.38743 0.153721 6.93928C-0.15496 8.49113 0.00346625 10.0997 0.608967 11.5615C1.21447 13.0233 2.23985 14.2727 3.55544 15.1518ZM4.40546 3.1204C5.46945 2.40946 6.72036 2.03 8 2.03C9.71595 2.03 11.3616 2.71166 12.575 3.92502C13.7883 5.13838 14.47 6.78405 14.47 8.5C14.47 9.77965 14.0905 11.0306 13.3796 12.0945C12.6687 13.1585 11.6582 13.9878 10.476 14.4775C9.29373 14.9672 7.99283 15.0953 6.73777 14.8457C5.48271 14.596 4.32987 13.9798 3.42502 13.075C2.52018 12.1701 1.90397 11.0173 1.65432 9.76224C1.40468 8.50718 1.5328 7.20628 2.0225 6.02404C2.5122 4.8418 3.34148 3.83133 4.40546 3.1204Z"
  });
  const path = setAttributesNS(createElementNS("path"), {
    d: "M6.68775 12.4297C6.78586 12.4745 6.89218 12.4984 7 12.5C7.11275 12.4955 7.22315 12.4664 7.32337 12.4145C7.4236 12.3627 7.51121 12.2894 7.58 12.2L12 5.63999C12.0848 5.47724 12.1071 5.28902 12.0625 5.11098C12.0178 4.93294 11.9095 4.77744 11.7579 4.67392C11.6064 4.57041 11.4221 4.52608 11.24 4.54931C11.0579 4.57254 10.8907 4.66173 10.77 4.79999L6.88 10.57L5.13 8.56999C5.06508 8.49566 4.98613 8.43488 4.89768 8.39111C4.80922 8.34735 4.713 8.32148 4.61453 8.31498C4.51605 8.30847 4.41727 8.32147 4.32382 8.35322C4.23038 8.38497 4.14413 8.43484 4.07 8.49999C3.92511 8.63217 3.83692 8.81523 3.82387 9.01092C3.81083 9.2066 3.87393 9.39976 4 9.54999L6.43 12.24C6.50187 12.3204 6.58964 12.385 6.68775 12.4297Z"
  });
  svg.appendChild(g).append(path, path2);
  const speakerDefs = createElementNS("defs");
  const speakerClipPathDef = setAttributesNS(createElementNS("clipPath"), {
    id: "clip0_57_156"
  });
  const speakerRect = setAttributesNS(createElementNS("rect"), {
    width: `${WIDTH}`,
    height: `${WIDTH}`,
    fill: "white",
    transform: "translate(0 0.5)"
  });
  speakerClipPathDef.appendChild(speakerRect);
  speakerDefs.appendChild(speakerClipPathDef);
  svg.appendChild(speakerDefs).appendChild(speakerClipPathDef).appendChild(speakerRect);
  return svg;
}

function Dialog({ open, onFormSubmitted, ...props }) {
  const options = props.options;
  const successIconHtml = T(() => ({ __html: SuccessIcon().outerHTML }), []);
  const [timeoutId, setTimeoutId] = d(null);
  const handleOnSuccessClick = q(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
    onFormSubmitted();
  }, [timeoutId]);
  const onSubmitSuccess = q(
    (data, eventId) => {
      props.onSubmitSuccess(data, eventId);
      setTimeoutId(
        setTimeout(() => {
          onFormSubmitted();
          setTimeoutId(null);
        }, SUCCESS_MESSAGE_TIMEOUT)
      );
    },
    [onFormSubmitted]
  );
  return /* @__PURE__ */ k$1(S, null, timeoutId ? /* @__PURE__ */ k$1("div", { class: "success__position", onClick: handleOnSuccessClick }, /* @__PURE__ */ k$1("div", { class: "success__content" }, options.successMessageText, /* @__PURE__ */ k$1("span", { class: "success__icon", dangerouslySetInnerHTML: successIconHtml }))) : /* @__PURE__ */ k$1("dialog", { class: "dialog", onClick: options.onFormClose, open }, /* @__PURE__ */ k$1("div", { class: "dialog__position" }, /* @__PURE__ */ k$1(
    "div",
    {
      class: "dialog__content",
      onClick: (e) => {
        e.stopPropagation();
      }
    },
    /* @__PURE__ */ k$1(DialogHeader, { options }),
    /* @__PURE__ */ k$1(Form, { ...props, onSubmitSuccess })
  ))));
}

const DIALOG = `
.dialog {
  position: fixed;
  z-index: var(--z-index);
  margin: 0;
  inset: 0;

  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 100vh;
  width: 100vw;

  color: var(--dialog-color, var(--foreground));
  fill: var(--dialog-color, var(--foreground));
  line-height: 1.75em;

  background-color: rgba(0, 0, 0, 0.05);
  border: none;
  inset: 0;
  opacity: 1;
  transition: opacity 0.2s ease-in-out;
}

.dialog__position {
  position: fixed;
  z-index: var(--z-index);
  inset: var(--dialog-inset);
  padding: var(--page-margin);
  display: flex;
  max-height: calc(100vh - (2 * var(--page-margin)));
}
@media (max-width: 600px) {
  .dialog__position {
    inset: var(--page-margin);
    padding: 0;
  }
}

.dialog__position:has(.editor) {
  inset: var(--page-margin);
  padding: 0;
}

.dialog:not([open]) {
  opacity: 0;
  pointer-events: none;
  visibility: hidden;
}
.dialog:not([open]) .dialog__content {
  transform: translate(0, -16px) scale(0.98);
}

.dialog__content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: var(--dialog-padding, 24px);
  max-width: 100%;
  width: 100%;
  max-height: 100%;
  overflow: auto;

  background: var(--dialog-background, var(--background));
  border-radius: var(--dialog-border-radius, 20px);
  border: var(--dialog-border, var(--border));
  box-shadow: var(--dialog-box-shadow, var(--box-shadow));
  transform: translate(0, 0) scale(1);
  transition: transform 0.2s ease-in-out;
}

`;
const DIALOG_HEADER = `
.dialog__header {
  display: flex;
  gap: 4px;
  justify-content: space-between;
  font-weight: var(--dialog-header-weight, 600);
  margin: 0;
}
.dialog__title {
  align-self: center;
  width: var(--form-width, 272px);
}

@media (max-width: 600px) {
  .dialog__title {
    width: auto;
  }
}

.dialog__position:has(.editor) .dialog__title {
  width: auto;
}


.brand-link {
  display: inline-flex;
}
.brand-link:focus-visible {
  outline: var(--outline);
}
`;
const FORM = `
.form {
  display: flex;
  overflow: auto;
  flex-direction: row;
  gap: 16px;
  flex: 1 0;
}

.form fieldset {
  border: none;
  margin: 0;
  padding: 0;
}

.form__right {
  flex: 0 0 auto;
  display: flex;
  overflow: auto;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  width: var(--form-width, 100%);
}

.dialog__position:has(.editor) .form__right {
  width: var(--form-width, 272px);
}

.form__top {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form__error-container {
  color: var(--error-color);
  fill: var(--error-color);
  width: 0;
  min-width: 100%;
  overflow-wrap: break-word;
}

.form__label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0px;
}

.form__label__text {
  display: flex;
  gap: 4px;
  align-items: center;
}

.form__label__text--required {
  font-size: 0.85em;
}

.form__input {
  font-family: inherit;
  line-height: inherit;
  background: transparent;
  box-sizing: border-box;
  border: var(--input-border, var(--border));
  border-radius: var(--input-border-radius, 6px);
  color: var(--input-color, inherit);
  fill: var(--input-color, inherit);
  font-size: var(--input-font-size, inherit);
  font-weight: var(--input-font-weight, 500);
  padding: 6px 12px;
}

.form__input::placeholder {
  opacity: 0.65;
  color: var(--input-placeholder-color, inherit);
  filter: var(--interactive-filter);
}

.form__input:focus-visible {
  outline: var(--input-focus-outline, var(--outline));
}

.form__input--textarea {
  font-family: inherit;
  resize: vertical;
}

.error {
  color: var(--error-color);
  fill: var(--error-color);
}
`;
const BUTTON = `
.btn-group {
  display: grid;
  gap: 8px;
}

.btn {
  line-height: inherit;
  border: var(--button-border, var(--border));
  border-radius: var(--button-border-radius, 6px);
  cursor: pointer;
  font-family: inherit;
  font-size: var(--button-font-size, inherit);
  font-weight: var(--button-font-weight, 600);
  padding: var(--button-padding, 6px 16px);
}
.btn[disabled] {
  opacity: 0.6;
  pointer-events: none;
}

.btn--primary {
  color: var(--button-primary-color, var(--accent-foreground));
  fill: var(--button-primary-color, var(--accent-foreground));
  background: var(--button-primary-background, var(--accent-background));
  border: var(--button-primary-border, var(--border));
  border-radius: var(--button-primary-border-radius, 6px);
  font-weight: var(--button-primary-font-weight, 500);
}
.btn--primary:hover {
  color: var(--button-primary-hover-color, var(--accent-foreground));
  fill: var(--button-primary-hover-color, var(--accent-foreground));
  background: var(--button-primary-hover-background, var(--accent-background));
  filter: var(--interactive-filter);
}
.btn--primary:focus-visible {
  background: var(--button-primary-hover-background, var(--accent-background));
  filter: var(--interactive-filter);
  outline: var(--button-primary-focus-outline, var(--outline));
}

.btn--default {
  color: var(--button-color, var(--foreground));
  fill: var(--button-color, var(--foreground));
  background: var(--button-background, var(--background));
  border: var(--button-border, var(--border));
  border-radius: var(--button-border-radius, 6px);
  font-weight: var(--button-font-weight, 500);
}
.btn--default:hover {
  color: var(--button-color, var(--foreground));
  fill: var(--button-color, var(--foreground));
  background: var(--button-hover-background, var(--background));
  filter: var(--interactive-filter);
}
.btn--default:focus-visible {
  background: var(--button-hover-background, var(--background));
  filter: var(--interactive-filter);
  outline: var(--button-focus-outline, var(--outline));
}
`;
const SUCCESS = `
.success__position {
  position: fixed;
  inset: var(--dialog-inset);
  padding: var(--page-margin);
  z-index: var(--z-index);
}
.success__content {
  background: var(--success-background, var(--background));
  border: var(--success-border, var(--border));
  border-radius: var(--success-border-radius, 1.7em/50%);
  box-shadow: var(--success-box-shadow, var(--box-shadow));
  font-weight: var(--success-font-weight, 600);
  color: var(--success-color);
  fill: var(--success-color);
  padding: 12px 24px;
  line-height: 1.75em;

  display: grid;
  align-items: center;
  grid-auto-flow: column;
  gap: 6px;
  cursor: default;
}

.success__icon {
  display: flex;
}
`;
function createDialogStyles(styleNonce) {
  const style = DOCUMENT.createElement("style");
  style.textContent = `
:host {
  --dialog-inset: var(--inset);
}

${DIALOG}
${DIALOG_HEADER}
${FORM}
${BUTTON}
${SUCCESS}
`;
  if (styleNonce) {
    style.setAttribute("nonce", styleNonce);
  }
  return style;
}

function getUser() {
  const currentUser = getCurrentScope().getUser();
  const isolationUser = getIsolationScope().getUser();
  const globalUser = getGlobalScope().getUser();
  if (currentUser && Object.keys(currentUser).length) {
    return currentUser;
  }
  if (isolationUser && Object.keys(isolationUser).length) {
    return isolationUser;
  }
  return globalUser;
}
const feedbackModalIntegration = (() => {
  return {
    name: "FeedbackModal",
    setupOnce() {
    },
    createDialog: ({ options, screenshotIntegration, sendFeedback, shadow }) => {
      const shadowRoot = shadow;
      const userKey = options.useSentryUser;
      const user = getUser();
      const el = DOCUMENT.createElement("div");
      const style = createDialogStyles(options.styleNonce);
      let originalOverflow = "";
      const dialog = {
        get el() {
          return el;
        },
        appendToDom() {
          if (!shadowRoot.contains(style) && !shadowRoot.contains(el)) {
            shadowRoot.appendChild(style);
            shadowRoot.appendChild(el);
          }
        },
        removeFromDom() {
          el.remove();
          style.remove();
          DOCUMENT.body.style.overflow = originalOverflow;
        },
        open() {
          renderContent(true);
          options.onFormOpen?.();
          getClient()?.emit("openFeedbackWidget");
          originalOverflow = DOCUMENT.body.style.overflow;
          DOCUMENT.body.style.overflow = "hidden";
        },
        close() {
          renderContent(false);
          DOCUMENT.body.style.overflow = originalOverflow;
        }
      };
      const screenshotInput = screenshotIntegration?.createInput({ h: k$1, hooks, dialog, options });
      const renderContent = (open) => {
        R(
          /* @__PURE__ */ k$1(
            Dialog,
            {
              options,
              screenshotInput,
              showName: options.showName || options.isNameRequired,
              showEmail: options.showEmail || options.isEmailRequired,
              defaultName: String(userKey && user?.[userKey.name] || ""),
              defaultEmail: String(userKey && user?.[userKey.email] || ""),
              onFormClose: () => {
                renderContent(false);
                options.onFormClose?.();
              },
              onSubmit: sendFeedback,
              onSubmitSuccess: (data, eventId) => {
                renderContent(false);
                options.onSubmitSuccess?.(data, eventId);
              },
              onSubmitError: (error) => {
                options.onSubmitError?.(error);
              },
              onFormSubmitted: () => {
                options.onFormSubmitted?.();
              },
              open
            }
          ),
          el
        );
      };
      return dialog;
    }
  };
});

function IconCloseFactory({
  h
  // eslint-disable-line @typescript-eslint/no-unused-vars
}) {
  return function IconClose() {
    return /* @__PURE__ */ h("svg", { "data-test-id": "icon-close", viewBox: "0 0 16 16", fill: "#2B2233", height: "25px", width: "25px" }, /* @__PURE__ */ h("circle", { r: "7", cx: "8", cy: "8", fill: "white" }), /* @__PURE__ */ h(
      "path",
      {
        strokeWidth: "1.5",
        d: "M8,16a8,8,0,1,1,8-8A8,8,0,0,1,8,16ZM8,1.53A6.47,6.47,0,1,0,14.47,8,6.47,6.47,0,0,0,8,1.53Z"
      }
    ), /* @__PURE__ */ h(
      "path",
      {
        strokeWidth: "1.5",
        d: "M5.34,11.41a.71.71,0,0,1-.53-.22.74.74,0,0,1,0-1.06l5.32-5.32a.75.75,0,0,1,1.06,1.06L5.87,11.19A.74.74,0,0,1,5.34,11.41Z"
      }
    ), /* @__PURE__ */ h(
      "path",
      {
        strokeWidth: "1.5",
        d: "M10.66,11.41a.74.74,0,0,1-.53-.22L4.81,5.87A.75.75,0,0,1,5.87,4.81l5.32,5.32a.74.74,0,0,1,0,1.06A.71.71,0,0,1,10.66,11.41Z"
      }
    ));
  };
}

function createScreenshotInputStyles(styleNonce) {
  const style = DOCUMENT.createElement("style");
  const surface200 = "#1A141F";
  const gray100 = "#302735";
  style.textContent = `
.editor {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
}

.editor__image-container {
  justify-items: center;
  padding: 15px;
  position: relative;
  height: 100%;
  border-radius: var(--menu-border-radius, 6px);

  background-color: ${surface200};
  background-image: repeating-linear-gradient(
      -145deg,
      transparent,
      transparent 8px,
      ${surface200} 8px,
      ${surface200} 11px
    ),
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 15px,
      ${gray100} 15px,
      ${gray100} 16px
    );
}

.editor__canvas-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editor__canvas-container > * {
  object-fit: contain;
  position: absolute;
}

.editor__tool-container {
  padding-top: 8px;
  display: flex;
  justify-content: center;
}

.editor__tool-bar {
  display: flex;
  gap: 8px;
}

.editor__tool {
  display: flex;
  padding: 8px 12px;
  justify-content: center;
  align-items: center;
  border: var(--button-border, var(--border));
  border-radius: var(--button-border-radius, 6px);
  background: var(--button-background, var(--background));
  color: var(--button-color, var(--foreground));
}

.editor__tool--active {
  background: var(--button-primary-background, var(--accent-background));
  color: var(--button-primary-color, var(--accent-foreground));
}

.editor__rect {
  position: absolute;
  z-index: 2;
}

.editor__rect button {
  opacity: 0;
  position: absolute;
  top: -12px;
  right: -12px;
  cursor: pointer;
  padding: 0;
  z-index: 3;
  border: none;
  background: none;
}

.editor__rect:hover button {
  opacity: 1;
}
`;
  if (styleNonce) {
    style.setAttribute("nonce", styleNonce);
  }
  return style;
}

function ToolbarFactory({
  h
  // eslint-disable-line @typescript-eslint/no-unused-vars
}) {
  return function Toolbar({
    action,
    setAction,
    options
  }) {
    return /* @__PURE__ */ h("div", { class: "editor__tool-container" }, /* @__PURE__ */ h("div", { class: "editor__tool-bar" }, /* @__PURE__ */ h(
      "button",
      {
        type: "button",
        class: `editor__tool ${action === "highlight" ? "editor__tool--active" : ""}`,
        onClick: () => {
          setAction(action === "highlight" ? "" : "highlight");
        }
      },
      options.highlightToolText
    ), /* @__PURE__ */ h(
      "button",
      {
        type: "button",
        class: `editor__tool ${action === "hide" ? "editor__tool--active" : ""}`,
        onClick: () => {
          setAction(action === "hide" ? "" : "hide");
        }
      },
      options.hideToolText
    )));
  };
}

function useTakeScreenshotFactory({ hooks }) {
  function useDpi() {
    const [dpi, setDpi] = hooks.useState(WINDOW.devicePixelRatio ?? 1);
    hooks.useEffect(() => {
      const onChange = () => {
        setDpi(WINDOW.devicePixelRatio);
      };
      const media = matchMedia(`(resolution: ${WINDOW.devicePixelRatio}dppx)`);
      media.addEventListener("change", onChange);
      return () => {
        media.removeEventListener("change", onChange);
      };
    }, []);
    return dpi;
  }
  return function useTakeScreenshot({ onBeforeScreenshot, onScreenshot, onAfterScreenshot, onError }) {
    const dpi = useDpi();
    hooks.useEffect(() => {
      const takeScreenshot = async () => {
        onBeforeScreenshot();
        const stream = await NAVIGATOR.mediaDevices.getDisplayMedia({
          video: {
            width: WINDOW.innerWidth * dpi,
            height: WINDOW.innerHeight * dpi
          },
          audio: false,
          // @ts-expect-error experimental flags: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getDisplayMedia#prefercurrenttab
          monitorTypeSurfaces: "exclude",
          preferCurrentTab: true,
          selfBrowserSurface: "include",
          surfaceSwitching: "exclude"
        });
        const video = DOCUMENT.createElement("video");
        await new Promise((resolve, reject) => {
          video.srcObject = stream;
          video.onloadedmetadata = () => {
            onScreenshot(video, dpi);
            stream.getTracks().forEach((track) => track.stop());
            resolve();
          };
          video.play().catch(reject);
        });
        onAfterScreenshot();
      };
      takeScreenshot().catch(onError);
    }, []);
  };
}

function drawRect(command, ctx, color) {
  switch (command.type) {
    case "highlight": {
      ctx.shadowColor = "rgba(0, 0, 0, 0.7)";
      ctx.shadowBlur = 50;
      ctx.fillStyle = color;
      ctx.fillRect(command.x - 1, command.y - 1, command.w + 2, command.h + 2);
      ctx.clearRect(command.x, command.y, command.w, command.h);
      break;
    }
    case "hide":
      ctx.fillStyle = "rgb(0, 0, 0)";
      ctx.fillRect(command.x, command.y, command.w, command.h);
      break;
  }
}
function with2dContext(canvas, options, callback) {
  if (!canvas) {
    return;
  }
  const ctx = canvas.getContext("2d", options);
  if (!ctx) {
    return;
  }
  callback(canvas, ctx);
}
function paintImage(maybeDest, source) {
  with2dContext(maybeDest, { alpha: true }, (destCanvas, destCtx) => {
    destCtx.drawImage(source, 0, 0, source.width, source.height, 0, 0, destCanvas.width, destCanvas.height);
  });
}
function paintForeground(maybeCanvas, strokeColor, drawCommands) {
  with2dContext(maybeCanvas, { alpha: true }, (canvas, ctx) => {
    if (drawCommands.length) {
      ctx.fillStyle = "rgba(0, 0, 0, 0.25)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    drawCommands.forEach((command) => {
      drawRect(command, ctx, strokeColor);
    });
  });
}
function ScreenshotEditorFactory({
  h: h2,
  hooks,
  outputBuffer,
  dialog,
  options
}) {
  const useTakeScreenshot = useTakeScreenshotFactory({ hooks });
  const Toolbar = ToolbarFactory({ h: h2 });
  const IconClose = IconCloseFactory({ h: h2 });
  const editorStyleInnerText = { __html: createScreenshotInputStyles(options.styleNonce).innerText };
  const dialogStyle = dialog.el.style;
  const ScreenshotEditor = ({ screenshot }) => {
    const [action, setAction] = hooks.useState("highlight");
    const [drawCommands, setDrawCommands] = hooks.useState([]);
    const measurementRef = hooks.useRef(null);
    const backgroundRef = hooks.useRef(null);
    const foregroundRef = hooks.useRef(null);
    const mouseRef = hooks.useRef(null);
    const [scaleFactor, setScaleFactor] = hooks.useState(1);
    const strokeColor = hooks.useMemo(() => {
      const sentryFeedback = DOCUMENT.getElementById(options.id);
      if (!sentryFeedback) {
        return "white";
      }
      const computedStyle = getComputedStyle(sentryFeedback);
      return computedStyle.getPropertyValue("--button-primary-background") || computedStyle.getPropertyValue("--accent-background");
    }, [options.id]);
    hooks.useLayoutEffect(() => {
      const handleResize = () => {
        const measurementDiv = measurementRef.current;
        if (!measurementDiv) {
          return;
        }
        with2dContext(screenshot.canvas, { alpha: false }, (canvas) => {
          const scale = Math.min(
            measurementDiv.clientWidth / canvas.width,
            measurementDiv.clientHeight / canvas.height
          );
          setScaleFactor(scale);
        });
        if (measurementDiv.clientHeight === 0 || measurementDiv.clientWidth === 0) {
          setTimeout(handleResize, 0);
        }
      };
      handleResize();
      WINDOW.addEventListener("resize", handleResize);
      return () => {
        WINDOW.removeEventListener("resize", handleResize);
      };
    }, [screenshot]);
    const setCanvasSize = hooks.useCallback(
      (maybeCanvas, scale) => {
        with2dContext(maybeCanvas, { alpha: true }, (canvas, ctx) => {
          ctx.scale(scale, scale);
          canvas.width = screenshot.canvas.width;
          canvas.height = screenshot.canvas.height;
        });
      },
      [screenshot]
    );
    hooks.useEffect(() => {
      setCanvasSize(backgroundRef.current, screenshot.dpi);
      paintImage(backgroundRef.current, screenshot.canvas);
    }, [screenshot]);
    hooks.useEffect(() => {
      setCanvasSize(foregroundRef.current, screenshot.dpi);
      with2dContext(foregroundRef.current, { alpha: true }, (canvas, ctx) => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      });
      paintForeground(foregroundRef.current, strokeColor, drawCommands);
    }, [drawCommands, strokeColor]);
    hooks.useEffect(() => {
      setCanvasSize(outputBuffer, screenshot.dpi);
      paintImage(outputBuffer, screenshot.canvas);
      with2dContext(DOCUMENT.createElement("canvas"), { alpha: true }, (foreground, ctx) => {
        ctx.scale(screenshot.dpi, screenshot.dpi);
        foreground.width = screenshot.canvas.width;
        foreground.height = screenshot.canvas.height;
        paintForeground(foreground, strokeColor, drawCommands);
        paintImage(outputBuffer, foreground);
      });
    }, [drawCommands, screenshot, strokeColor]);
    const handleMouseDown = (e) => {
      if (!action || !mouseRef.current) {
        return;
      }
      const boundingRect = mouseRef.current.getBoundingClientRect();
      const startingPoint = {
        type: action,
        x: e.offsetX / scaleFactor,
        y: e.offsetY / scaleFactor};
      const getDrawCommand = (startingPoint2, e2) => {
        const x = (e2.clientX - boundingRect.x) / scaleFactor;
        const y = (e2.clientY - boundingRect.y) / scaleFactor;
        return {
          type: startingPoint2.type,
          x: Math.min(startingPoint2.x, x),
          y: Math.min(startingPoint2.y, y),
          w: Math.abs(x - startingPoint2.x),
          h: Math.abs(y - startingPoint2.y)
        };
      };
      const handleMouseMove = (e2) => {
        with2dContext(foregroundRef.current, { alpha: true }, (canvas, ctx) => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
        paintForeground(foregroundRef.current, strokeColor, [...drawCommands, getDrawCommand(startingPoint, e2)]);
      };
      const handleMouseUp = (e2) => {
        const drawCommand = getDrawCommand(startingPoint, e2);
        if (drawCommand.w * scaleFactor >= 1 && drawCommand.h * scaleFactor >= 1) {
          setDrawCommands((prev) => [...prev, drawCommand]);
        }
        DOCUMENT.removeEventListener("mousemove", handleMouseMove);
        DOCUMENT.removeEventListener("mouseup", handleMouseUp);
      };
      DOCUMENT.addEventListener("mousemove", handleMouseMove);
      DOCUMENT.addEventListener("mouseup", handleMouseUp);
    };
    const deleteRect = hooks.useCallback((index) => {
      return (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDrawCommands((prev) => {
          const updatedRects = [...prev];
          updatedRects.splice(index, 1);
          return updatedRects;
        });
      };
    }, []);
    const dimensions = {
      width: `${screenshot.canvas.width * scaleFactor}px`,
      height: `${screenshot.canvas.height * scaleFactor}px`
    };
    const handleStopPropagation = (e) => {
      e.stopPropagation();
    };
    return /* @__PURE__ */ h2("div", { class: "editor" }, /* @__PURE__ */ h2("style", { nonce: options.styleNonce, dangerouslySetInnerHTML: editorStyleInnerText }), /* @__PURE__ */ h2("div", { class: "editor__image-container" }, /* @__PURE__ */ h2("div", { class: "editor__canvas-container", ref: measurementRef }, /* @__PURE__ */ h2("canvas", { ref: backgroundRef, id: "background", style: dimensions }), /* @__PURE__ */ h2("canvas", { ref: foregroundRef, id: "foreground", style: dimensions }), /* @__PURE__ */ h2("div", { ref: mouseRef, onMouseDown: handleMouseDown, style: dimensions }, drawCommands.map((rect, index) => /* @__PURE__ */ h2(
      "div",
      {
        key: index,
        class: "editor__rect",
        style: {
          top: `${rect.y * scaleFactor}px`,
          left: `${rect.x * scaleFactor}px`,
          width: `${rect.w * scaleFactor}px`,
          height: `${rect.h * scaleFactor}px`
        }
      },
      /* @__PURE__ */ h2(
        "button",
        {
          "aria-label": options.removeHighlightText,
          onClick: deleteRect(index),
          onMouseDown: handleStopPropagation,
          onMouseUp: handleStopPropagation,
          type: "button"
        },
        /* @__PURE__ */ h2(IconClose, null)
      )
    ))))), /* @__PURE__ */ h2(Toolbar, { options, action, setAction }));
  };
  return function Wrapper({ onError }) {
    const [screenshot, setScreenshot] = hooks.useState();
    useTakeScreenshot({
      onBeforeScreenshot: hooks.useCallback(() => {
        dialogStyle.display = "none";
      }, []),
      onScreenshot: hooks.useCallback((screenshotVideo, dpi) => {
        with2dContext(DOCUMENT.createElement("canvas"), { alpha: false }, (canvas, ctx) => {
          ctx.scale(dpi, dpi);
          canvas.width = screenshotVideo.videoWidth;
          canvas.height = screenshotVideo.videoHeight;
          ctx.drawImage(screenshotVideo, 0, 0, canvas.width, canvas.height);
          setScreenshot({ canvas, dpi });
        });
        outputBuffer.width = screenshotVideo.videoWidth;
        outputBuffer.height = screenshotVideo.videoHeight;
      }, []),
      onAfterScreenshot: hooks.useCallback(() => {
        dialogStyle.display = "block";
      }, []),
      onError: hooks.useCallback((error) => {
        dialogStyle.display = "block";
        onError(error);
      }, [])
    });
    if (screenshot) {
      return /* @__PURE__ */ h2(ScreenshotEditor, { screenshot });
    }
    return /* @__PURE__ */ h2("div", null);
  };
}

const feedbackScreenshotIntegration = (() => {
  return {
    name: "FeedbackScreenshot",
    setupOnce() {
    },
    createInput: ({ h, hooks, dialog, options }) => {
      const outputBuffer = DOCUMENT.createElement("canvas");
      return {
        input: ScreenshotEditorFactory({
          h,
          hooks,
          outputBuffer,
          dialog,
          options
        }),
        // eslint-disable-line @typescript-eslint/no-explicit-any
        value: async () => {
          const blob = await new Promise((resolve) => {
            outputBuffer.toBlob(resolve, "image/png");
          });
          if (blob) {
            const data = new Uint8Array(await blob.arrayBuffer());
            const attachment = {
              data,
              filename: "screenshot.png",
              contentType: "application/png"
              // attachmentType?: string;
            };
            return attachment;
          }
          return void 0;
        }
      };
    }
  };
});

export { buildFeedbackIntegration, feedbackModalIntegration, feedbackScreenshotIntegration, getFeedback, sendFeedback };
//# sourceMappingURL=index.js.map
