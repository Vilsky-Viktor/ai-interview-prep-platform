import { getClient, startInactiveSpan } from '@sentry/browser';
import { hasSpanStreamingEnabled, UI_MOUNT_SPAN_NAME_FALLBACK, SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN, timestampInSeconds, withActiveSpan, UI_UPDATE_SPAN_NAME_FALLBACK, spanToJSON, UI_RENDER_SPAN_NAME_FALLBACK } from '@sentry/core';
import { SENTRY_DESCRIPTION, UI_COMPONENT_NAME, SENTRY_OP } from '@sentry/conventions/attributes';
import { UI_MOUNT, UI_UPDATE, UI_RENDER } from '@sentry/conventions/op';
import * as React from 'react';
import { hoistNonReactStatics } from './hoist-non-react-statics.js';

const UNKNOWN_COMPONENT = "unknown";
class Profiler extends React.Component {
  constructor(props) {
    super(props);
    const { name, disabled = false } = this.props;
    if (disabled) {
      return;
    }
    const client = getClient();
    const hasSpanStreaming = !!client && hasSpanStreamingEnabled(client);
    const description = `<${name}>`;
    const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
    this._mountSpan = startInactiveSpan({
      name: hasSpanStreaming ? componentName || UI_MOUNT_SPAN_NAME_FALLBACK : description,
      onlyIfParent: true,
      attributes: {
        [SENTRY_OP]: UI_MOUNT,
        [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
        ...componentName && { [UI_COMPONENT_NAME]: componentName },
        ...hasSpanStreaming && { [SENTRY_DESCRIPTION]: description }
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
        const now = timestampInSeconds();
        this._updateSpan = withActiveSpan(this._mountSpan, () => {
          const client = getClient();
          const hasSpanStreaming = !!client && hasSpanStreamingEnabled(client);
          const description = `<${this.props.name}>`;
          const componentName = this.props.name === UNKNOWN_COMPONENT ? void 0 : this.props.name;
          return startInactiveSpan({
            name: hasSpanStreaming ? componentName || UI_UPDATE_SPAN_NAME_FALLBACK : description,
            onlyIfParent: true,
            startTime: now,
            attributes: {
              [SENTRY_OP]: UI_UPDATE,
              [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
              ...componentName && { [UI_COMPONENT_NAME]: componentName },
              "ui.react.changed_props": changedProps,
              ...hasSpanStreaming && { [SENTRY_DESCRIPTION]: description }
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
    const endTimestamp = timestampInSeconds();
    const { name, includeRender = true } = this.props;
    if (this._mountSpan && includeRender) {
      const startTime = spanToJSON(this._mountSpan).end_timestamp;
      withActiveSpan(this._mountSpan, () => {
        const client = getClient();
        const hasSpanStreaming = !!client && hasSpanStreamingEnabled(client);
        const description = `<${name}>`;
        const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
        const renderSpan = startInactiveSpan({
          onlyIfParent: true,
          name: hasSpanStreaming ? componentName || UI_RENDER_SPAN_NAME_FALLBACK : description,
          startTime,
          attributes: {
            [SENTRY_OP]: UI_RENDER,
            [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
            ...componentName && { [UI_COMPONENT_NAME]: componentName },
            ...hasSpanStreaming && { [SENTRY_DESCRIPTION]: description }
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
  hoistNonReactStatics(Wrapped, WrappedComponent);
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
    const client = getClient();
    const hasSpanStreaming = !!client && hasSpanStreamingEnabled(client);
    const description = `<${name}>`;
    const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
    return startInactiveSpan({
      name: hasSpanStreaming ? componentName || UI_MOUNT_SPAN_NAME_FALLBACK : description,
      onlyIfParent: true,
      attributes: {
        [SENTRY_OP]: UI_MOUNT,
        [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
        ...componentName && { [UI_COMPONENT_NAME]: componentName },
        ...hasSpanStreaming && { [SENTRY_DESCRIPTION]: description }
      }
    });
  });
  React.useEffect(() => {
    if (mountSpan) {
      mountSpan.end();
    }
    return () => {
      if (mountSpan && options.hasRenderSpan) {
        const startTime = spanToJSON(mountSpan).end_timestamp;
        const endTimestamp = timestampInSeconds();
        const client = getClient();
        const hasSpanStreaming = !!client && hasSpanStreamingEnabled(client);
        const description = `<${name}>`;
        const componentName = name === UNKNOWN_COMPONENT ? void 0 : name;
        const renderSpan = startInactiveSpan({
          name: hasSpanStreaming ? componentName || UI_RENDER_SPAN_NAME_FALLBACK : description,
          onlyIfParent: true,
          startTime,
          attributes: {
            [SENTRY_OP]: UI_RENDER,
            [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: "auto.ui.react.profiler",
            ...componentName && { [UI_COMPONENT_NAME]: componentName },
            ...hasSpanStreaming && { [SENTRY_DESCRIPTION]: description }
          }
        });
        if (renderSpan) {
          renderSpan.end(endTimestamp);
        }
      }
    };
  }, []);
}

export { Profiler, UNKNOWN_COMPONENT, useProfiler, withProfiler };
//# sourceMappingURL=profiler.js.map
