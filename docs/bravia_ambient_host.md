# Bravia ambient display host

The [Bravia Ambient Display](https://github.com/lachlanw-117/Bravia-Ambient-Display)
is a separate companion project. It owns the Android TV app, photo/weather host,
add-on packaging and tests. This repository records the household dependencies
and deployment procedure rather than keeping another copy of that code.

The TV owns screensaver entry and dismissal. No HA automation or timer is needed
to launch it, and no TV-control service is required for the host.

## Enhancement phases and current scope

On 8 November 2026, the user selected separately approved implementation phases.
The companion [roadmap](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/main/ROADMAP.md),
[decision log](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/main/DECISIONS.md)
and [maintenance procedure](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/main/MAINTENANCE.md)
own the phase definitions and rationale. The user separately approved committing,
pushing and merging this documentation during repository consolidation. Bravia
remains private; those links require access. Publishing is a separate decision.

Phase 0 is repository documentation only. Phase 1 BOM work was subsequently
authorised and trial-deployed from its branch as recorded below. The design B photo layout,
native HA notice foundation, TV interactions, phone migration and additional
attention sources remain later phases requiring their own authorisation. Design C
aircraft work requires a separate implementation plan. No automatic progression,
live change, device cleanup, commit, push or merge is implied by accepting the
roadmap. Keep household entity/routing definitions here and reusable source in
Bravia.

Future notice categories, destination switches, pauses and private inbox belong
in HA. Definitions and logic belong in Git; restored helper values are everyday
runtime preferences, so changing a routing switch does not create a source edit
to reconcile later. These helpers and sources have not been implemented. Initial
sources will be washing, backups and one aggregated update count, in capture-only
mode. Existing washing phone notifications and the laundry-light action stay in
place until individually reviewed migration. Repairs, persistent notifications
and selected device-health rules follow later, without raw log/state forwarding.

## BOM source inspection - 8 November 2026

Read-only inspection of the installed manifest, adapter source and selected
entity-registry metadata found:

| Item | Recorded finding |
|---|---|
| Component | `bureau_of_meteorology`, version 1.4.0 |
| Daily weather | `weather.weather_homemascot`; selected target for Phase 1 |
| Hourly weather | `weather.weather_homemascot_hourly`; not the daily-forecast target |
| Observation source | Sydney Airport temperature, humidity and wind sensors |
| Collection interval | Five minutes in installed source |
| Existing weather | `weather.forecast_home`, registry platform `met` |

This identifies entities and source ownership, not current readings or a successful
forecast response. The attempted Supervisor API path returned 401. No saved app
options or credential files were opened, and no weather selection was changed.
The last recorded host deployment still used `weather.forecast_home`; the current
live selection has not been reverified.

Phase 1 must verify BOM availability, attribution, current readings, today's daily
forecast and Sydney date/freshness handling before a separately approved source
change. Do not silently substitute another provider or remove Met.no from HA.
Preserve the working connection and key without printing or rotating it.

## Phase 1 local implementation - 8 November 2026

The user authorised Phase 1 investigation and local implementation. Work is on
Bravia `feature/bom-weather` and HA `docs/bom-weather`. The user subsequently
approved committing/pushing both branches and opening PRs on 8 November. Merge,
deployment and TV verification were separate decisions; the subsequently approved
trial is recorded below. Source baseline is Bravia
`69ee6877d00eb263ed1c125a273d722639256e31`, HA
`ec3c7b650a6df906c6fb3064de75f0999b2246cd`.

Read-only authenticated browser inspection at approximately 12:01 Sydney time:

- `weather.weather_homemascot`: `rainy`, 15.5°C.
- Attribution: `Data provided by the Australian Bureau of Meteorology`.
- `condition_source: daily`; HA last updated 00:54:55 UTC and last reported
  00:59:54 UTC on 8 November. These are HA reporting timestamps, not independently
  verified station observation timestamps.
- Daily `weather.get_forecasts` retrieval succeeded. Today's row was
  `datetime: '2026-11-08T00:00:00'`, `temperature: 19`, `templow: 11`, `rainy`.
  The next row was 9 November, high 20 / low 12. The actual response confirms
  offset-free local dates and HA-normalised `temperature`/`templow` fields.

This supersedes the earlier inability to verify the entity through the Supervisor
API. The browser check does not establish what the current Bravia host selects;
saved host options were not read or changed. No HA configuration was changed.

The reusable [Phase 1 implementation and acceptance record](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/main/PHASE1.md)
contains the reviewed scope. It covers the local-date fix, cache source isolation,
attribution decisions, live checks and rollback. Initial local validation passed 13 host tests,
packaged-server syntax, Android build/signature verification and 15 JVM assertions.

The proposed scope, subsequently approved for the branch trial below: update only the Bravia host package, change
its `weather_entity` option to `weather.weather_homemascot` while concealing and
preserving the existing key, then install the reviewed matching TV APK. Preserve
the album, settings and current/previous recovery artifacts. Do not remove Met.no,
change the BOM integration, reload/restart HA core or progress to Phase 2. Record
exact source/artifact hashes and TV acceptance after a named deployment approval.

## Phase 1 branch trial - 8 November 2026

The user approved the trial and selected **feature branch -> PR/local checks ->
approved trial deployment -> relevant device acceptance -> documented closeout ->
merge approval -> main** as the ongoing workflow. Both AGENTS files and development
workflows now carry that gate. Documentation-only work needs review/local checks,
not a device deployment. PRs remain open while acceptance is incomplete.

Pre-trial checks found no package drift: the installed host matched source
`3fbb12727382c538e43fdef125de39687d20bc07`. The actual TV APK was pulled privately;
SHA-256 `91509f1492ded58e6c87c0b357654e4607993b1fa5ef1e567a44b3b82fd88fd6`
matched the preserved previous local APK.

Recovery artifacts created before replacement:

- Pi package: `/backup/bravia-package-pre-phase1-20261108` (config, Dockerfile,
  previous server). Previous server SHA-256
  `41d8d66f6916379242c984421bfb7679e115c2aff8aeebd5d37c538de98f94fc`.
- Private Bravia-only app backup: `bravia-pre-phase1-20261108`, slug `edccffdd`.
  Its contents were not opened or exported; keep it private.
- Actual previous TV APK: Bravia ignored
  `build/phase1-trial-2026-11-08/previous-installed.apk`.

Approved host deployment: branch revision
`fe1e045470613f323b31acebb8266fd7fe9ccde5`, server SHA-256
`9af7ed17c1da5446749ad2d8ae34b5c757eee494e2815777891a62118a2c2d80`.
Only `server.mjs` changed in the package; config/Dockerfile hashes stayed identical.
The Bravia app was stopped/rebuilt and started after saving
`weather_entity: weather.weather_homemascot` in the masked credential UI. Existing
key, timezone, photos, caches and unrelated apps were preserved. No HA core restart,
reload, BOM integration change or Met.no removal occurred.

LAN health returned HTTP 200 with `{"ok":true}`; unauthenticated weather returned
401. An initial localhost check within Terminal's container returned 404 because
it addressed the wrong namespace; LAN checks above establish the actual result.

The initial TV build installed successfully and its readback hash matched.
At about 12:16 Australia/Sydney, a private local screenshot showed photo playback,
16°C Rainy, high 19° / low 11° and the full BOM attribution sentence. This verifies
authenticated host weather arriving on the TV without reading the access key.
The user found that sentence intrusive, so the PR was kept open and revised.

The compact-credit APK, source
`c9f61305bc461796e6f1f5c082bff266c3f5ff4c`, then installed successfully. Its pulled
SHA-256 is `f3f78784e1b4856c14248dd8a2d90cc7084f0ccabfd1352a06916c70e7b60d2a`.
It displays `Bureau of Meteorology` at 60% of the main text size; the feed retains
the full attribution. Android build/signature and 18 JVM assertions passed; host
code remains identical to the 13-test pass and the deployed host hash.

At this intermediate trial point, pending checks were compact-credit acceptance, physical remote Back dismissal,
ordinary idle entry and debugging-disabled playback/exit. At inspection, Developer
options and ADB were enabled; service and persistent ADB TCP port properties were
5555. Session closeout is not yet recorded as complete. Historical streaming,
paused-video, HDMI, power, midnight/DST and failure/recovery checks remain unverified.
No deliberate failure simulation or TV restart was performed.

The compact credit was observed in the actual `AmbientDream` through the Sony
launcher Screensaver shortcut, with `mCurrentDreamIsTest=false`. The user then
explicitly requested **no visible credit**. The final candidate removes it while
retaining attribution in the feed/docs; final acceptance is recorded below.
This overrides the original visible-attribution design, not the BOM source choice.

Before that final feedback arrived, closeout disabled `adb_enabled`. The TV
refused changing `persist.adb.tcp.port` from 5555; disabling ADB dropped the session
and a TCP 5555 check returned ECONNREFUSED. Developer options master remains on;
unrelated developer settings were not changed. Debugging-disabled ordinary use
has not been confirmed. The user was asked to briefly re-enable USB/ADB debugging
for the final no-credit APK; the user did so and the installation succeeded.
Do not treat this testing session as closed until final acceptance and cleanup.

Final TV source: `dc050af8b911351eeee66f522fb15f1958536080`; installed APK SHA-256
`141cf96345e011098247c9c9ab05eee7d85e7e83c53a1a0e2f5cd8e131eeb7d8`, verified by
pulling installed bytes. Android build/signature verification and 15 JVM assertions
passed. The host remains on the previously verified unchanged server hash. The
user reported the no-credit display "looks right". Debugging was disabled again
with `adb_enabled: 0`, and TCP 5555 again returned ECONNREFUSED. The user then
answered "its all good" to the explicit Back-dismissal and normal idle/photo-return
check with debugging off. Those physical results are user-reported. Scoped Phase 1
acceptance and closeout passed; no merge has been performed or approved.

Developer options master remains enabled to preserve unreviewed settings. The
persistent port property remains 5555 because the TV refused changing it; whether
debugging stays disabled after a reboot is untested. A future approved maintenance
session should enable USB/ADB debugging through Developer options, deliberately
verify the listener/connection, then close it again after acceptance. No reboot,
factory reset or unrelated developer-setting change was made here. Historical
HDMI/streaming/power and failure/recovery tests remain unverified and are not
claimed as part of this focused weather acceptance.

Rollback, if needed and approved: restore only the preserved host package, rebuild
and start the Bravia app, restore `weather.forecast_home` through the concealed UI,
and reinstall the preserved matching signed APK with `install -r`. Preserve app
settings and album. The private app backup is retained if package rollback is
insufficient; do not expose it or clear app data. Record rollback verification.

## Phase 1 merge and Phase 2 trial - 8 November 2026

Phase 1 was accepted and merged following separate user approval. The user then
approved Phase 2 implementation, its TV trial, commits, pushes and PRs.
Bravia [PR #3](https://github.com/lachlanw-117/Bravia-Ambient-Display/pull/3)
and companion [PR #6](https://github.com/lachlanw-117/Wright-Home-Assistant/pull/6)
remain open; Phase 2 merge is not approved.

The photo-presentation trial is installed. The user liked the initial design and
requested a brighter background and **60 seconds per scene**. Both adjustments
are applied. The first brightness adjustment was still too dark, so the current
trial uses a warm cream background and dark text, following user feedback. The
interval remains configurable from 10 to 300 seconds. Portrait
pairing is enabled. Landscape and square photographs continue to display alone,
fitted in full. A live landscape scene is not yet explicitly recorded.

Local build/signature checks, 215 Android assertions and runtime-source CI passed.
Portrait pairs, single-photo mode and injected Back exit were checked on the TV.
Short performance samples are encouraging but do not establish long-run stability.
Final cream-palette acceptance, debugging closeout and ordinary idle/physical Back
checks remain pending. Debugging is currently enabled for final review.

No household configuration, host, photo-library or cache changes are part of this
phase. Detailed source/artifact identities, private recovery inventory and measured
trial evidence remain in the companion implementation record. No private photos
or testing artifacts are published here. Keep both PRs open until acceptance,
then request separate merge approval.

## Historical initial trial status

The initial photo-free results below are historical. The later first-album
deployment supersedes their zero-photo and source-revision details. These records
do not prove the current live state.

On 7 November 2026, the debug APK was installed on the Sony TV through ADB.
The user confirmed that the app was visible and the screensaver was working as
expected. This is a user-reported result, not a recorded pass for every streaming,
paused-video, HDMI, remote-button or power scenario.

The Pi host was installed and started on 7 November 2026 from companion commit
`b05ca1f6bbf3f8151c950150ac5cdd7bb5dbd826`, version 0.1.0, as
`local_bravia_ambient`. The three generated package files were SHA-256 verified
after transfer. Live inspection found no previous Bravia package or photo folder;
no existing installation files were replaced. The Pi runs HA OS 18.4 on aarch64,
with Core 2026.11.0. Its existing Terminal & SSH app supplied the deployment route;
the connected HA tool's Supervisor requests returned 401.

Recorded checks at approximately 22:08–22:10 Australia/Sydney:

- LAN `http://192.168.0.142:8099/health`: HTTP 200, `{"ok":true}`.
- Unauthenticated `/weather`: HTTP 401.
- Authenticated `/weather`: 15.1°C, `partlycloudy`, today's high 15.1°C and
  low 14.4°C for 7 November; `stale: false`, `forecastStale: false`.
- `/share/bravia-ambient` and the authenticated photo manifest: zero photos.
- TV at `192.168.0.152`, Android 12: host settings saved; Preview visibly showed
  **Weather: Feed received**, **15°C partlycloudy**, **High 15° Low 14°**.
  The rounded readings agree with the host. **No album cached** is expected here.

At approximately 22:18 Australia/Sydney, the user-approved weather-label APK
from companion commit `8e4e856` was installed over the existing TV app with ADB
`install -r` (Success). Preview showed **Weather: Feed received**,
**15°C Partly cloudy**, **High 15° Low 14°**. The saved connection survived the
update. This TV-only change required no host update or HA core restart.

A random 32-byte key was configured directly and transferred to the TV without
printing it or committing it. No HA core restart, merge, photo import or cache
implementation change was performed. Failure/recovery, system-picker availability
and individual playback/HDMI/input acceptance checks remain unverified. See the
companion project's [trial guide](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/main/TRIAL.md).

The current app retains a photo cache on the TV. Persistent offline photo storage
is no longer a user requirement; removing it is a future app change. The installed
APK still uses the existing cache implementation.

## First album deployment — 7 November 2026

With explicit approval, host and TV were updated from source commit
`3fbb12727382c538e43fdef125de39687d20bc07` to accept up to 250 photos.
The 8 MiB per-photo and 256 MiB album limits and cache implementation are unchanged.
All 11 synthetic host tests passed, including 147/250 acceptance and 251 rejection
without replacing the last-good manifest. Android build, APK verification and the
15 existing JVM assertions passed before deployment.

The user's local export contained 147 still photos (65 JPEG and 82 HEIC) and
29 MP4 files. HEICs were converted locally to oriented JPEG copies; existing JPEGs
were copied byte-for-byte. MP4s were excluded; their possible Live Photo pairing
was not independently confirmed. The source ZIP remains untouched outside Git.
All 147 output photos decoded locally and are distinct: 219,526,548 bytes total
(209.36 MiB), largest 5,986,670 bytes (5.71 MiB). No resizing was necessary.

All 147 transferred files matched local SHA-256 checksums before publication to
`/share/bravia-ambient`. The previous host package is preserved locally on the Pi
at `/backup/bravia-package-b05ca1f`; a local app backup was created before rebuild.
Only the Bravia app was stopped/rebuilt/started; HA core was not restarted.
The matching TV APK installed with ADB `install -r` (Success).
Authenticated host manifest and source folder both contain 147 photos, and the
weather feed remained fresh. The first TV download took several minutes with the
infrastructure waiting screen visible. The user then confirmed that photos were
appearing. This confirms visible photo playback, not a complete review of all
147 photos, orientation, crossfades or offline/failure recovery. Screenshot capture
returned empty data during this phase, so playback confirmation is user-reported.

## Dependencies

| Item | Required value or behaviour |
|---|---|
| Host machine | Home Assistant OS on the household Raspberry Pi 5 |
| App source | Companion repository; generate the local app package there |
| Architecture | Package supports aarch64 and amd64; verify the host architecture before installation |
| Weather entity | Phase 1 branch trial: `weather.weather_homemascot`; prior selector `weather.forecast_home` retained for rollback |
| Forecast | Daily forecast through `weather.get_forecasts`; current state alone does not prove today's high/low is available |
| Timezone | `Australia/Sydney` |
| LAN port | TCP 8099, reachable from the TV; check for conflicts before installation |
| Source folder | `/share/bravia-ambient`, mounted read-only; 147 photos recorded at the first album deployment; an empty folder is only for a new photo-free trial |
| Host cache | App-private `/data/cache`; separate from source files and Git |
| Access key | Random value of at least 24 characters, entered locally in app options and TV setup |
| HA authentication | Supervisor-provided token, used only by the installed host; never entered on the TV |

Keep photos, keys, app options, runtime data and signing material out of both
repositories. Do not expose port 8099 to the internet. LAN HTTP sends the host key
and feed without encryption; use an existing suitable HTTPS proxy if available.

## Install and check

Installation and starting the host were approved in the trial session on
7 November 2026, along with keeping GitHub updated. The deployment completed as
recorded above. Future deployments, reloads and device actions require approval within
their named scope; approval is not a completed deployment result.

1. Review the selected companion source revision and record its commit ID and any
   local changes. From that checkout, run `npm.cmd test` on Windows (`npm test` on
   other platforms), then `node tools/package-addon.mjs`.
2. Check the live host for existing installation files, port conflicts and the
   weather entity. Preserve any existing installation before replacing files.
3. Copy only the generated `build/bravia_ambient` directory into HA OS's
   local-app directory (`/local_apps/` in Terminal & SSH on HA OS 18.4; older
   instructions refer to `/addons/`). Reload the local app inventory and install
   **Bravia Ambient Photo Host**. This generated package stays outside this repo.
4. Set `access_key` locally, `weather_entity: weather.forecast_home` and
   `time_zone: Australia/Sydney` in app options. Start the host. Do not paste the
   key or full options into chat, logs or version control.
5. From a LAN browser, open `http://PI_ADDRESS:8099/health`. Expect
   `{"ok":true}`. This proves reachability, not authentication or HA weather.
   An absent photo folder may produce a photo-sync warning during this trial.
6. Enter the host URL and key in Wright Ambient on the TV. Save and reopen
   **Preview photos**. Expect **Weather: Feed received**. An empty photo feed may
   still show **No album cached**; that is not an authentication result.
7. Check real temperature, condition and today's high/low. Missing readings after
   a received feed require checking the host-to-HA path. Avoid sharing raw logs
   until reviewed for sensitive values.
8. With separate approval for stop/start actions, check failure and recovery.
   Clock/date should continue locally; aged cached weather must be marked stale.
   Refresh runs on entry and every five minutes while the screen is running.

These steps describe the initial installation. Do not repeat them just to resume
development or apply the Phase 1 source change. Use an approved UI that keeps the
credential field concealed to change only the approved weather selector. Do not
inspect/export full saved app options or print/rotate the existing key.

Record each result before adding a small exported album. The photo-free trial
does not validate photo decoding, crossfades or offline photo playback.

## Update and roll back

Review and test a specific companion revision before each update. Record the
currently installed revision, preserve the previous generated package and use a
local backup for app options/data. Backups may contain the access key and must
stay outside Git. Recheck live drift before replacing anything.

With approval, stop the host, replace only its reviewed package files, rebuild
through HA's local app workflow as required, and start it. Repeat reachability,
authenticated TV feed and weather checks. Configuration and data compatibility
must be reviewed before restoring a previous package or app backup.

To abandon the host trial, stop the app with approval. On the TV, restore the
original system screensaver if desired. Uninstalling or clearing app data is a
separate decision and can remove saved settings/cache. Source photos remain
untouched. No HA core configuration change or core restart is part of this plan.

## Session closeout and recovery inventory

Follow the companion maintenance procedure after each approved TV testing window.
Disable ADB/network debugging, review the Developer options master switch and
confirm ordinary playback, idle entry and remote exit with debugging disabled.
Normal app use does not need ADB. Phase 1 closeout on 8 November disabled ADB and
verified TCP 5555 refused connections; ordinary use was confirmed by the user.
Developer options master remains enabled; reboot persistence is untested. See the
branch-trial record above. Disconnecting the development computer alone is not
the closeout action.

The earlier historical host package is `/backup/bravia-package-b05ca1f`. A private
app backup was made before the album-limit update. Current/previous APKs and their
signing material remain outside Git. Verify recovery artifacts and hashes before
relying on them; do not inspect credential-bearing backup contents or delete them
as cleanup. Source revision `3fbb12727382c538e43fdef125de39687d20bc07` identifies
the earlier matching host/TV deployment. Phase 1 source identities, verified hashes
and current recovery copies are recorded in the branch-trial section above.

Do not clear caches/app data, remove photos or signing material, apply
skinny-bravia, disable Terminal & SSH or relocate shared toolchains as part of
routine cleanup. Source/tool changes and deletions need their own scoped review.
