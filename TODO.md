# TODO

This is a working household configuration, with a few things still worth improving.
These are planned changes, not claims about behaviour already implemented.

## Automation reliability

- [ ] **Handle stale kiosk battery readings.** Charging starts at 40% and stops
  at 80%. The fallback handles unknown/unavailable readings, but misses a numeric
  reading that stops updating. Establish a reliable reporting timestamp and
  timeout, then prioritise stale or missing feedback over the thresholds.
  An unchanged percentage is not proof that reporting stopped, and an integration
  may republish cached data. Check startup, missing entities, stale high readings
  and plug recovery.
- [ ] **Avoid extra washer-cleaning reminders.** Notify on a genuine numeric count
  increase reaching 30 and each wash after that. Ignore attribute-only updates,
  downward corrections and counter resets. Decide whether reconnection should
  remind again; the proposed default is no. Check 29 to 30, 30 to 31, unknown
  to 30 and reset to zero. Attempt both notification recipients independently.
- [ ] **Confirm bathroom button behaviour.** Both short-press buttons currently
  toggle the lights. Decide whether to keep that or give them dedicated on/off actions.
- [ ] **Quote the dashboard's hidden Off label.** Home Assistant parses the
  unquoted value as boolean false. The name is hidden, so this is metadata cleanup.

## Configuration coverage

- [x] Import the two UI-created automations and preserve the bathroom remote and
  disabled washer-completion trigger edits. All 20 automation definitions were
  compared with the live API on 7 November 2026.
- [x] Add the deployed black-fan controls and feedback templates to version control.
  Validation and limitations are recorded in the [technical notes](docs/arlec_black_fan_dashboard_notes.md).
- [ ] Compare full live script definitions with `scripts.yaml`; matching
  inventory counts alone do not establish matching behaviour.
- [ ] Export and review the UI-managed Our Home and Fridge dashboards. Decide which
  should be maintained as YAML and which should have documented exports.
- [ ] Document the source of the eight Tuya fan scenes. They exist live but have no
  definitions in `scenes.yaml`; check whether the integration supplies them before
  attempting to recreate them.
- [ ] Inventory helpers, integration settings, blueprints and custom components.
  Record what belongs in Git and what must be recreated through the UI.
- [ ] Compare remaining non-secret configuration before claiming the whole
  installation is in sync.

## Completing a fix

Keep reliability changes separate from capturing existing behaviour. For each fix,
review the diff, run meaningful local checks, and document limitations.
Before an approved deployment, recheck live drift and back up affected files.
The [development workflow](docs/local_development_workflow.md) covers validation
and rollback. Credentials, authentication state, databases and backups stay out of Git.
