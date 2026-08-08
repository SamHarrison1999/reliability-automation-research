# Technical event-record contract

The Phase 2 fit probe writes one JSON object per line. Every record contains:

- `event_id` — unique within the emitting component and run;
- `run_id` — unique identifier for the execution;
- `scenario_id` — versioned scenario identifier;
- `source_component` — service or controller emitting the event;
- `event_type` — controlled event name;
- `timestamp` — UTC event timestamp;
- `trace_id` — correlation identifier;
- `software_version` — emitting component version;
- `telemetry_contract` — structured telemetry contract identifier for service events.

Fault, deployment and workload records add explicit target, phase, version, outcome or latency fields as applicable. Raw records are technical feasibility evidence only. They must not contain participant identifiers, real payment information or production traffic.
