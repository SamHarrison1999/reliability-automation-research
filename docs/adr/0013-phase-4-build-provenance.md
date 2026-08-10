# ADR 0013: Pin Phase 4 prototype build provenance

**Status:** Accepted

**Date:** 2026-08-10

## Context

Phase 4 must demonstrate that the smallest OrderFlow benchmark can be built, deployed, reset and observed reproducibly. The existing container packaging used `python:3.12-slim` as its base image. A tag is human-readable but mutable: the content resolved by that tag can change independently of this repository.

A validation run could therefore record the repository commit and manifest hashes while still rebuilding against different base-image content. That weakens the build-provenance chain and makes later reproduction harder to audit.

On the accepted Docker Desktop target, `python:3.12-slim` was resolved on 2026-08-10 to:

`python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36`

The pulled image reported Linux/amd64, while Docker Desktop reported a Linux x86_64 engine.

## Decision

Phase 4 container builds will pin the Python base image by immutable repository digest while retaining the `3.12-slim` tag in the reference for readability.

The prototype manifest records:

- the readable base-image tag;
- the immutable digest;
- the complete pinned image reference; and
- the declared `linux/amd64` build platform.

The Dockerfile and prototype manifest must agree on the complete pinned base-image reference. Automated contract tests enforce this relationship.

Updating the base image later is an explicit provenance change. The new digest must be reviewed, recorded in the repository and validated before it is used for new reproducibility evidence.

## Consequences

### Positive

- a repository revision identifies the exact external base-image input used by the Phase 4 build;
- later validation can distinguish source-code changes from base-image changes;
- the build-provenance record can include both readable version intent and immutable content identity; and
- accidental movement of `python:3.12-slim` cannot silently change the Phase 4 prototype build.

### Trade-offs

- refreshing the Python base image becomes an intentional repository change;
- reproducing the build requires access to the pinned digest from a registry or local cache; and
- the accepted Phase 4 build is explicitly platform-bounded rather than architecture-neutral.

## Evidence boundary

Pinning an image digest improves reproducibility of the build input. It is not evidence that the prototype has already been reproduced, that reliability improved, or that the system is production-ready.

Those claims remain outside Phase 4 or require the later validation evidence defined by the Phase 4 research-design record.
