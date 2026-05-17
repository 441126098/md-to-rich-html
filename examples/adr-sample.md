# ADR 0007: Use Server-Sent Events instead of WebSockets for live updates

## Status

Accepted (2024-11-18)

## Context

The dashboard needs to push live metric updates to thousands of concurrent
clients. Two natural candidates: WebSockets and Server-Sent Events (SSE).

WebSockets give us bidirectional streaming. SSE is one-way (server → client)
but uses ordinary HTTP, which means:

- Works behind every proxy and load balancer we already operate
- No special handshake to debug
- Auto-reconnect is built into the browser's `EventSource` API
- We can scale it the same way we scale our existing HTTPS endpoints

The downside of SSE is that the client cannot push back over the same channel.
For our use case the client only needs to *receive* — any commands go through
the regular REST API.

## Decision

We will use SSE for all live dashboard updates. WebSockets remain on the table
for future features that require true bidirectional streaming (e.g. collaborative
editing), but they will not be introduced for this feature.

## Consequences

**Positive.** Simpler ops story. No new infrastructure. Browser-native
reconnection. Easier to observe — every event is a normal HTTP response.

**Negative.** Cannot multiplex many event streams over one connection like
WebSockets can. We accept this; if it bites us we can revisit.

**Neutral.** Mobile clients use the same `EventSource` polyfills already
shipping in the app today.
