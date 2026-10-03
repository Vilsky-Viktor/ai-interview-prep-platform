Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

const browser = require('@sentry/browser');
const core = require('@sentry/core');
const attributes = require('@sentry/conventions/attributes');
const op = require('@sentry/conventions/op');
const React = require('react');
const hoistNonReactStatics = require('./hoist-non-react-statics.js');

const UNKNOWN_COMPONENT = "unknown";
class Profiler extends React.Component {
  constructor(props) {
    super(props);
    const { name, disabled = false } = this.props;
    if (disabled) {
      return;
    }
    const client = browser.getClient();
    const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
    const description = `<${name}>`;
    const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
    this._mountSpan = browser.startInactiveSpan({
      name: hasSpanStreaming ? componentName || core.UI_MOUNT_SPAN_NAME_FALLBACK : description,
      onlyIfParent: true,
      attributes: {
        [attributes.SENTRY_OP]: op.UI_MOUNT,
        [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
        ...componentName && { [attributes.UI_COMPONENT_NAME]: componentName },
        ...hasSpanStreaming && { [attributes.SENTRY_DESCRIPTION]: description }
      }
    });
  }
  // If a component mounted, we can finish the mount activity.
  componentDidMount() {
    if (this._mountSpan) {
      this._mountSpan.end();
    }
  }
  shouldComponentUpdate({ updateProps, includeUpdates = true }) {
    if (includeUpdates && this._mountSpan && updateProps !== this.props.updateProps) {
      const changedProps = Object.keys(updateProps).filter((k) => updateProps[k] !== this.props.updateProps[k]);
      if (changedProps.length > 0) {
        const now = core.timestampInSeconds();
        this._updateSpan = core.withActiveSpan(this._mountSpan, () => {
          const client = browser.getClient();
          const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
          const description = `<${this.props.name}>`;
          const componentName = this.props.name === UNKNOWN_COMPONENT ? void 0 : this.props.name;
          return browser.startInactiveSpan({
            name: hasSpanStreaming ? componentName || core.UI_UPDATE_SPAN_NAME_FALLBACK : description,
            onlyIfParent: true,
            startTime: now,
            attributes: {
              [attributes.SENTRY_OP]: op.UI_UPDATE,
              [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
              ...componentName && { [attributes.UI_COMPONENT_NAME]: componentName },
              "ui.react.changed_props": changedProps,
              ...hasSpanStreaming && { [attributes.SENTRY_DESCRIPTION]: description }
            }
          });
        });
      }
    }
    return true;
  }
  componentDidUpdate() {
    if (this._updateSpan) {
      this._updateSpan.end();
      this._updateSpan = void 0;
    }
  }
  // If a component is unmounted, we can say it is no longer on the screen.
  // This means we can finish the span representing the component render.
  componentWillUnmount() {
    const endTimestamp = core.timestampInSeconds();
    const { name, includeRender = true } = this.props;
    if (this._mountSpan && includeRender) {
      const startTime = core.spanToJSON(this._mountSpan).end_timestamp;
      core.withActiveSpan(this._mountSpan, () => {
        const client = browser.getClient();
        const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
        const description = `<${name}>`;
        const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
        const renderSpan = browser.startInactiveSpan({
          onlyIfParent: true,
          name: hasSpanStreaming ? componentName || core.UI_RENDER_SPAN_NAME_FALLBACK : description,
          startTime,
          attributes: {
            [attributes.SENTRY_OP]: op.UI_RENDER,
            [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
            ...componentName && { [attributes.UI_COMPONENT_NAME]: componentName },
            ...hasSpanStreaming && { [attributes.SENTRY_DESCRIPTION]: description }
          }
        });
        if (renderSpan) {
          renderSpan.end(endTimestamp);
        }
      });
    }
  }
  render() {
    return this.props.children;
  }
}
Object.assign(Profiler, {
  defaultProps: {
    disabled: false,
    includeRender: true,
    includeUpdates: true
  }
});
function withProfiler(WrappedComponent, options) {
  const componentDisplayName = options?.name || WrappedComponent.displayName || WrappedComponent.name || UNKNOWN_COMPONENT;
  const Wrapped = (props) => /* @__PURE__ */ React.createElement(Profiler, { ...options, name: componentDisplayName, updateProps: props }, /* @__PURE__ */ React.createElement(WrappedComponent, { ...props }));
  Wrapped.displayName = `profiler(${componentDisplayName})`;
  hoistNonReactStatics.hoistNonReactStatics(Wrapped, WrappedComponent);
  return Wrapped;
}
function useProfiler(name, options = {
  disabled: false,
  hasRenderSpan: true
}) {
  const [mountSpan] = React.useState(() => {
    if (options?.disabled) {
      return void 0;
    }
    const client = browser.getClient();
    const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
    const description = `<${name}>`;
    const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
    return browser.startInactiveSpan({
      name: hasSpanStreaming ? componentName || core.UI_MOUNT_SPAN_NAME_FALLBACK : description,
      onlyIfParent: true,
      attributes: {
        [attributes.SENTRY_OP]: op.UI_MOUNT,
        [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
        ...componentName && { [attributes.UI_COMPONENT_NAME]: componentName },
        ...hasSpanStreaming && { [attributes.SENTRY_DESCRIPTION]: description }
      }
    });
  });
  React.useEffect(() => {
    if (mountSpan) {
      mountSpan.end();
    }
    return () => {
      if (mountSpan && options.hasRenderSpan) {
        const startTime = core.spanToJSON(mountSpan).end_timestamp;
        const endTimestamp = core.timestampInSeconds();
        const client = browser.getClient();
        const hasSpanStreaming = !!client && core.hasSpanStreamingEnabled(client);
        const description = `<${name}>`;
        const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
        const renderSpan = browser.startInactiveSpan({
          name: hasSpanStreaming ? componentName || core.UI_RENDER_SPAN_NAME_FALLBACK : description,
          onlyIfParent: true,
          startTime,
          attributes: {
            [attributes.SENTRY_OP]: op.UI_RENDER,
            [core.SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
            ...componentName && { [attributes.UI_COMPONENT_NAME]: componentName },
            ...hasSpanStreaming && { [attributes.SENTRY_DESCRIPTION]: description }
          }
        });
        if (renderSpan) {
          renderSpan.end(endTimestamp);
        }
      }
    };
  }, []);
}

exports.Profiler = Profiler;
exports.UNKNOWN_COMPONENT = UNKNOWN_COMPONENT;
exports.useProfiler = useProfiler;
exports.withProfiler = withProfiler;
//# sourceMappingURL=profiler.js.map
