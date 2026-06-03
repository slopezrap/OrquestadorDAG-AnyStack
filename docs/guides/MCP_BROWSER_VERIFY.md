# Web/mobile MCP verification policy

`/verify-slice` must use the visual MCP that matches the declared product surface. The verifier must make a small health call before trusting any listed MCP.

- **Web / browser / Flutter web:** use an accepted browser MCP. Priority: `chrome-devtools`, then `claude-in-chrome`, then `agent360-browser-mcp` / `browser-mcp`.
- **Flutter mobile:** use Dart/Flutter MCP with `MCP_CLIENT: dart|flutter|flutter-driver` and `VISUAL_CHECK_METHOD: simulator|emulator|device`. Browser MCP is valid for Flutter web only.

## Web/browser MCPs and priority

| Priority | MCP | Use when | Isolation model |
|---:|-----|----------|-----------------|
| 1 | Chrome DevTools MCP (`chrome-devtools`) | Default for React/Flutter web verification, including network/console/performance inspection and auth/MFA when a visible isolated/per-task Chrome can be used | Prefer MCP configured with `--isolated`; for parallel per-slice runs, start Chrome with `scripts/chrome-devtools-isolated-session.sh --task <TASK_ID> --start` and connect MCP via `--browser-url=<url>`. |
| 2 | Claude-in-Chrome MCP (`claude-in-chrome`) | Human-visible fallback when Chrome DevTools MCP is locked/unusable or cannot complete the required human session | Real user Chrome; avoid parallel slices unless the user controls the session. |
| 3 | Agent360 Browser MCP (`agent360-browser-mcp` / `browser-mcp`) | Third fallback for real Chrome sessions, cookies, MFA/2FA, CAPTCHA, user permissions or human-in-the-loop when the first two are unusable | Real Chrome session with MCP session/tab-group isolation. Do not force repo-managed Chrome profiles for this MCP. |

Do not use Playwright/browser-use as the normal web/browser `/verify-slice` gate. They can be project-specific support tools, but they do not replace accepted browser MCP proof unless the user explicitly waives human web verification.

## Flutter mobile MCP

Flutter mobile verification applies when `STACK_PROFILE.yaml` declares Flutter plus a mobile surface, for example:

```yaml
frontend:
  framework: flutter
  visual_check: simulator
verification:
  mobile:
    enabled: true
    visual_check_method: simulator
    mcp_client: dart
```

The verified handoff must include:

```text
MCP_BROWSER: not_applicable:flutter_mobile
MCP_CLIENT: dart|flutter|flutter-driver
VISUAL_CHECK_METHOD: simulator|emulator|device
SIMULATOR_DEVICE: <real device id/name or auto>
FLUTTER_MCP_HEALTH: passed
```

Recommended setup:

```bash
claude mcp add --transport stdio dart -- dart mcp-server
```

A Flutter mobile slice must not be closed with browser-only evidence. If Dart/Flutter MCP or the simulator/device is unavailable, block with `BLOCKER_REASON: flutter_mobile_mcp_unavailable` and rerun `/verify-slice <TASK_ID>` after connecting the MCP/device.

## Chrome DevTools isolation helper

```bash
bash scripts/chrome-devtools-isolated-session.sh --task <TASK_ID>
bash scripts/chrome-devtools-isolated-session.sh --task <TASK_ID> --url http://localhost:5173 --start
```

The helper prints:

```text
CHROME_DEVTOOLS_PROFILE
CHROME_DEVTOOLS_REMOTE_DEBUGGING_PORT
CHROME_DEVTOOLS_BROWSER_URL
MCP_CONFIG_HINT: chrome-devtools-mcp --browser-url=<url>
```

It does not kill Chrome and does not edit Claude Code MCP config. It gives a safe per-`TASK_ID` profile/port for environments that configure Chrome DevTools MCP in `--browser-url` mode.

## Web/browser selection rule

1. Try Chrome DevTools MCP first, even for login/MFA flows if the task can use a visible isolated/per-task Chrome. Pause for user MFA/2FA/CAPTCHA input if required, then continue through DevTools.
2. If Chrome DevTools MCP is blocked by a profile lock or is listed but unusable, run `bash scripts/chrome-mcp-doctor.sh || true` once and show the isolated-session helper output.
3. If DevTools cannot be made usable without user action, try `claude-in-chrome`.
4. If `claude-in-chrome` is not usable, try Agent360/`browser-mcp`.
5. Once one MCP completes the human reproduction, do not re-run another MCP just because it is listed or broken.

## Failure policy

If all browser MCP candidates are listed but unusable for a web/browser slice, `slice-verifier` must append a final blocked `## verify-slice` section with:

```text
MCP_BROWSER: unavailable
VERIFY_OUTCOME: blocked
BLOCKER_REASON: browser_mcp_unavailable
MCP_DIAGNOSTIC: listed_but_unusable|stale_profile_lock|not_listed|...
USER_ACTION_REQUIRED: connect/restart Chrome DevTools MCP first; if locked, use scripts/chrome-mcp-doctor.sh and scripts/chrome-devtools-isolated-session.sh --task <TASK_ID>; if DevTools cannot be used, connect claude-in-chrome; if that cannot be used, connect Agent360 Browser MCP (browser-mcp); rerun /verify-slice <TASK_ID>
```

If Flutter mobile MCP or the simulator/device is unavailable, the blocked section must identify the mobile gate:

```text
MCP_BROWSER: not_applicable:flutter_mobile
MCP_CLIENT: unavailable
VISUAL_CHECK_METHOD: simulator|emulator|device
VERIFY_OUTCOME: blocked
BLOCKER_REASON: flutter_mobile_mcp_unavailable
USER_ACTION_REQUIRED: connect Dart/Flutter MCP, start an available simulator/emulator/device, then rerun /verify-slice <TASK_ID>
```

These are mechanical blockers, not product follow-ups.

## Lifecycle placement in DAG mode

Do not kill or restart browser MCPs from `/next-wave`. Do not kill or restart browser/mobile MCPs from `/next-wave`. `next-wave` can run while other terminals/worktrees are still using visible browser sessions or simulators, so process-level MCP cleanup there is too aggressive.

Safe placement:

- `/next-wave`: compact agent memories, flush deferred worktree cleanup, sync lifecycle events, compute ready frontier. No MCP process control.
- `/verify-slice` / `slice-verifier`: perform the correct web/mobile MCP preflight, diagnose Chrome DevTools profile locks for browser verification with `scripts/chrome-mcp-doctor.sh`, and block cleanly if no accepted MCP path is usable.
- Manual recovery: close/restart the affected MCP/browser/simulator session yourself, then rerun `/verify-slice <TASK_ID>`. The orchestrator should not kill Chrome, simulators or MCP server processes automatically.

This avoids one slice breaking another slice's MFA/login/browser/simulator verification in a parallel DAG run.
