# Contributor and Automation Directives

Use these project-specific rules when making changes with a coding assistant or by hand.

## Source of truth

- `flows/smart-fishing.json` defines deployed flow behavior.
- `compose.yaml`, `.env.example`, `node-red/package.json`, and `node-red/settings.js` define the runtime, dependencies, and configuration.
- `docs/implementation_plan.md` defines phase status. Mark a task complete only after the feature exists and its verification has been performed.
- The README, specification, architecture, and technology stack documents must describe current behavior accurately and label planned work as planned.

## Implementation conventions

- Keep credentials and machine-specific settings in the ignored `.env`; document variable names and safe defaults in `.env.example`.
- Preserve normalized message contracts and topics unless intentionally changing them; update dependent nodes and documentation together.
- Validate external data before downstream use. Represent unavailable measurements explicitly and preserve useful provider timestamps.
- Keep request construction, HTTP transport, normalization, and error reporting as understandable flow steps.
- Add an npm or Python dependency only when implemented code uses it. Pin runtime/dependency versions and document their purpose.
- Do not describe a dashboard, MQTT broker, simulator, chart, or sensor as implemented until its code and configuration exist.
- Preserve local development security defaults: loopback binding and no secrets in tracked files.

## Change completion

Inspect the diff, validate edited JSON/YAML and flow references, and update relevant documentation and checklist items. For changes affecting the running flow, verify behavior through Node-RED and its Debug sidebar when the service is available. Do not commit or push unless requested.
