# Go Language Justification

## Why Go

I chose Go because it produces small, static binaries, compiles quickly, and has a minimal standard library that already covers HTTP servers. That makes it a good fit for a tiny service and for multi‑stage Docker builds later in the course.

## Tradeoffs

- **Pros:** fast compile/run, simple deployment, good concurrency model, no runtime dependency chain.
- **Cons:** less dynamic than Python for quick iteration, and JSON struct definitions add some boilerplate.
