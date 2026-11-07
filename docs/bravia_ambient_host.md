# Bravia ambient display host

The [Bravia Ambient Display](https://github.com/lachlanw-117/Bravia-Ambient-Display)
is a separate companion project. It owns the Android TV app, photo/weather host,
add-on packaging and tests. This repository records the household dependencies
and deployment procedure rather than keeping another copy of that code.

The TV owns screensaver entry and dismissal. No HA automation or timer is needed
to launch it, and no TV-control service is required for the host.

## Trial status

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
companion project's [trial guide](https://github.com/lachlanw-117/Bravia-Ambient-Display/blob/feature/bravia-ambient/TRIAL.md).

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
| Weather entity | `weather.forecast_home`; verify it still exists before deployment |
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
