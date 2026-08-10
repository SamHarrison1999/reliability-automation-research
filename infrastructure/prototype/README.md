# OrderFlow Phase 4 prototype

This directory declares the smallest versioned technical prototype carried into Phase 4. It promotes the already-tested two-service OrderFlow feasibility slice into an explicit research object without changing its business behaviour.

## Boundary

The prototype contains `order-api` and `inventory`. `order-api` accepts deterministic synthetic order requests and calls `inventory`. The prototype reuses the existing Dockerfile and entrypoint so Phase 4 does not duplicate packaging that was already validated during feasibility work.

`orderflow-phase-4.json` is the source configuration for prototype identity, topology, service versions, packaging inputs and evidence boundary. Kubernetes deployment configuration and reproducibility execution are added in later Phase 4 slices.

## Evidence rule

The manifest is research infrastructure/configuration, not an experiment result. Its presence does not demonstrate reproducible deployment, reliability improvement, production readiness or any empirical effect.
