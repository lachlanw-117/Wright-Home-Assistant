# TODO

This is a working household configuration, with a few things still worth improving.
Checked items are completed as described; unchecked items remain planned work.

The charging, washer-reminder and hidden-label fixes were deployed on
7 November 2026 after configuration validation and an approved automation reload.
Their source changes are on `feature/ha-automation-reliability`.
See [reliability notes](docs/automation_reliability.md) for decisions and checks.

## Automation reliability

- [x] **Handle stale kiosk battery readings.** Charging starts at 40% and stops
  at 80%. The previous fallback missed numeric readings that stopped updating.
  The deployed watchdog uses `last_reported` with
  a one-hour timeout and prioritises stale or missing feedback over the thresholds.
  An unchanged percentage is not proof that reporting stopped, and an integration
  may republish cached data. Local checks cover startup inputs, missing entities,
  stale high readings and plug recovery.
- [x] **Avoid extra washer-cleaning reminders.** Notify on a genuine numeric count
  increase reaching 30 and each wash after that. Ignore attribute-only updates,
  downward corrections and counter resets. Reconnection does not remind again.
  Local checks cover 29 to 30, 30 to 31, unknown to 30 and reset to zero.
  Delivery errors for one recipient do not prevent attempting the other.
- [ ] **Confirm bathroom button behaviour.** Both short-press buttons currently
  toggle the lights. Decide whether to keep that or give them dedicated on/off actions.
- [x] **Quote the dashboard's hidden Off label.** The deployed value is a string.
  The name is hidden, so this is metadata cleanup.
- [ ] Observe the charging watchdog over a longer period and review its one-hour
  timeout. Notification delivery and simulated device-failure tests remain unperformed.

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
- [x] Document the source of the eight Tuya fan scenes. The live entity registry
  identifies all eight as `tuya` integration entities. They should not be
  duplicated in `scenes.yaml`. See [configuration dependencies](docs/configuration_dependencies.md).
- [ ] Inventory helpers, integration settings, blueprints and custom components.
  Record what belongs in Git and what must be recreated through the UI.
  The two lighting-time helpers have been recorded; the wider inventory remains open.
- [ ] Compare remaining non-secret configuration before claiming the whole
  installation is in sync.

## Completing a fix

Keep reliability changes separate from capturing existing behaviour. For each fix,
review the diff, run meaningful local checks, and document limitations.
Before an approved deployment, recheck live drift and back up affected files.
The [development workflow](docs/local_development_workflow.md) covers validation
and rollback. Credentials, authentication state, databases and backups stay out of Git.
