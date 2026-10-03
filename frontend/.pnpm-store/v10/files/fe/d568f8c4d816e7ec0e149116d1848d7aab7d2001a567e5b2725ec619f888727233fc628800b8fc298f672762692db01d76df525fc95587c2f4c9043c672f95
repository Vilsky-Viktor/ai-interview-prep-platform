import type { Span } from '@sentry/core';
import type { MutableRootSpan } from '../../server/enhanceHandleRequestRootSpan';
/**
 * Adapts a live `Span` to the `MutableRootSpan` shape the root-span enhancers operate on.
 *
 * The enhancers run in a `spanEnd` hook (before the span is serialized/frozen), so their writes flow
 * into both the legacy transaction event and the streamed span JSON without a separate code path.
 *
 * `setName` is deliberately not `span.updateName()`: `updateName` stamps `sentry.source: 'custom'` as a
 * side effect, which would clobber the source the enhancers set (or a `route`/`url` source hoisted at
 * span start). We preserve the current source across the rename so only explicit source writes take effect.
 */
export declare function createLiveRootSpanAdapter(span: Span): MutableRootSpan;
//# sourceMappingURL=liveRootSpanAdapter.d.ts.map