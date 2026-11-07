# Local Home Assistant development

This repository supports a live household installation. The aim is to make
useful, maintainable changes without surprising anyone using the house.
`AGENTS.md` contains the working rules. Repository files, GitHub and live HA
must be checked separately; none automatically proves what is in the others.

## Git and review

The setup and black-fan work was done on local branch `feature/codex-ha-setup`.
The cached black-fan branch was inspected without switching to it or merging it.
Its existing scene actions were reused, and missing feedback sensors were added
to version-controlled YAML instead of creating duplicate helpers through the UI.

Keep changes small. Inspect the existing implementation first, preserve unrelated
working-tree changes, run appropriate local checks and show the diff. Do not stage,
commit, push or merge as an incidental part of deployment. Nothing from this work
had been staged or committed when this document was written.

## MCP for inspection and explicit actions

Codex connects directly to the third-party npm package
`@jarahkon/hass-mcp-server@1.0.10` over STDIO. This is not Home Assistant's official
MCP server. Neither Home Assistant VS Code extension is needed for this connection;
both were left disabled. Node.js LTS was installed on the development computer.

The project `.codex/config.toml` launches a local PowerShell wrapper under
`%LOCALAPPDATA%\CodexHomeAssistant\`. This machine-specific setup is not a portable
installation recipe; review it separately before committing or sharing it.
The wrapper uses the local HA address and passes the token through the child
process environment. It does not configure the server's optional SSH access.

The token was entered by Lachlan in a separate hidden-input PowerShell window
and stored using Windows DPAPI under his user profile, outside the repository.
The launcher decrypts it at runtime; the agent does not inspect or print it.
Encryption protects storage, not against processes already able to run as that
Windows user. Never paste tokens into chat or put them in repository files.

The server exposes write tools as well as reads. Instructions and chat approvals
guide their use; they are not an enforced read-only security boundary. Connections
and actions must be deliberate and within the user's authorised task. Live data
returned by tools becomes part of the AI conversation, even with a local server.

The limited source review found that the WebSocket client disables TLS certificate
validation. The current connection uses local HTTP; no router ports or public HA
exposure were added. This review was not a dependency audit or proof that npm
package contents match the public source.

## SSH for file comparison, backup and deployment

HA's existing Terminal & SSH app was initially stopped. Lachlan started it.
Authentication uses the Bitwarden desktop SSH agent and the existing HA key,
imported by Lachlan into an SSH-key vault item. The private key is not exported
to the repository or read by the agent. Bitwarden controls key-use authorisation.

Use Windows OpenSSH with agent authentication, password authentication disabled,
agent forwarding disabled and no private identity file. The server's public host
key was recorded on the first connection; subsequent connections use strict
host-key checking. Do not suppress a changed-host-key warning.

SSH access was used only for named configuration files, hashes and `ha core check`.
Do not browse secrets, credentials, private keys, runtime storage or unrelated
files. Keep backup files outside Git; they can contain household configuration.

## Deploy deliberately

1. Inspect the local implementation and relevant live state. Ask before device
   tests and agree on the state to restore afterward.
2. Prepare and validate the local change. Explain behaviour, limitations and diff.
3. Obtain explicit approval for the named deployment and any required reload.
   An approval for one change does not cover later revisions or device tests.
4. Recheck live files for changes and take timestamped local backups.
5. Upload only the approved files. If templates change, run HA configuration
   validation before reloading them. Restore backups if validation fails.
6. Compare deployed and local hashes, inspect the resulting entities/dashboard,
   and ask Lachlan to check the phone layout and physical behaviour where needed.

Dashboard-only YAML changes need a dashboard refresh, not a template reload or
HA restart. Template reloads affect all YAML template entities, including the
existing Dyson and party feedback; they require approval even for a small change.
Restarts, pushes and merges remain separate approval decisions.

Use the saved live files for rollback, not an assumed GitHub version. Restore only
the affected files, validate and perform the approved reload/refresh. Stop if live
files have changed unexpectedly rather than overwriting somebody else's work.

The [black-fan implementation notes](arlec_black_fan_dashboard_notes.md) record
the verified mappings, test results and backup directories for this change.
