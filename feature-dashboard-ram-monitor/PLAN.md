# AI Agent Plan — DASHBOARD RAM Monitor + CLUSTER Plugin

**Branch:** `feature/dashboard-ram-monitor`
**Base:** `DASHBOARD-0.1v-linux-native`
**Repo:** `/home/ficus-pro/Documents/DASHBOARD`
**Date:** 2026-09-13

---

## Goal

Add RAM monitoring to the DASHBOARD app with three windows inside the main window:
1. **7-Day Avg RAM** — average used RAM over the last 7 days
2. **30-Day Avg RAM** — average used RAM over the last 30 days
3. **CLUSTER Plugin** — optional; when installed, shows aggregated RAM from connected CLUSTER root nodes

CLUSTER integration is **optional and plugin-based**. The app must run identically without it.

---

## Architecture

```
00_app/
  00_main.py              ← edited: start RAM sampler at boot
  08_ram_sampler.py       ← NEW: /proc/meminfo thread, 10s interval, SQLite WAL
  09_ram_aggregator.py    ← NEW: get_average_ram(days), get_series(days, limit)
  10_ram_window.py        ← NEW: create_ram_panels() → 3 Gtk.Box panels
  window.py               ← edited: append panels below toggle button
  plugins/
    __init__.py           ← NEW: plugin loader
    cluster/
      __init__.py         ← NEW: entry point
      plugin.py           ← NEW: init(ctx) → registers panel, starts polling
      discover.py         ← NEW: UDP/mDNS discovery of CLUSTER roots
      connect.py          ← NEW: fetch http://<ip>:8080/api/status → parse workers
      panel.py            ← NEW: create_cluster_panel() → Gtk.Box

04_data/
  ram_data.db             ← runtime, gitignored (SQLite)
  plugins/
    cluster/              ← runtime plugin dir (symlink or copy)

09_tests/
  test_ram_sampler.py     ← NEW
  test_ram_aggregator.py  ← NEW
  test_ram_window.py      ← NEW
  test_cluster_plugin.py  ← NEW
```

---

## Hard Constraints

- GTK4 / PyGObject only — no PyQt, no PySide in new code
- Every function in its own file, every file in its own folder
- License header on every file: `# SPDX-License-Identifier: GPL-3.0-or-later`
- Type hints on all function signatures
- No hardcoded absolute paths — use `Path(__file__)` relative
- No new external dependencies (stdlib `sqlite3`, `socket`, `threading`, `urllib`, `/proc/meminfo`)
- Numbered files: `00_` = entry, `_99` = quit; new files use `08_`–`10_`

---

## Execution Pipeline

Each phase is a separate commit.

```
Phase 0  Pre-flight & branch setup
Phase 1  RAM sampler core (08_ram_sampler.py)
Phase 2  Aggregation queries (09_ram_aggregator.py)
Phase 3  Panel UI (10_ram_window.py)
Phase 4  Window + main integration (window.py, 00_main.py edits)
Phase 5  Plugin system skeleton (plugins/__init__.py)
Phase 6  CLUSTER plugin (plugins/cluster/*.py)
Phase 7  Tests (09_tests/)
Phase 8  Commit & push
Phase 9  README + branch map update
```

---

## Phase 0 — Pre-flight (DONE)

- [x] Branch `feature/dashboard-ram-monitor` created from `DASHBOARD-0.1v-linux-native`
- [x] Working tree clean (stashed)
- [x] Plan directory created at `feature-dashboard-ram-monitor/`

---

## Phase 1 — RAM Sampler (`00_app/08_ram_sampler.py`)

**Function signature:**
```python
def start_ram_sampler(
    db_path: Path,
    callback: Callable[[dict], None],
    interval_ms: int = 10000,
) -> threading.Thread:
    ...
```

**Logic:**
1. Open SQLite in WAL mode, create `ram_samples(ts INTEGER PRIMARY KEY, used_mb REAL, total_mb REAL)` with index on `ts`
2. Purge rows where `ts < now() - 30*86400` on startup
3. Spawn daemon thread:
   - Read `/proc/meminfo`: parse `MemTotal` and `MemAvailable` (kB)
   - Compute `used_mb = (MemTotal - MemAvailable) / 1024`, `total_mb = MemTotal / 1024`
   - INSERT into SQLite
   - Call `callback({"used_mb": ..., "total_mb": ..., "ts": ...})`
   - `time.sleep(interval_ms / 1000)`
4. Every 3600s, re-run purge job
5. Return the thread object

**Test:** `test_ram_sampler.py` mocks `/proc/meminfo`, verifies DB row count and interval.

---

## Phase 2 — Aggregator (`00_app/09_ram_aggregator.py`)

**Functions:**
```python
def get_average_ram(db_path: Path, days: int) -> float | None:
    """Return AVG(used_mb) for the last N days, or None if no data."""

def get_series(db_path: Path, days: int, limit: int = 200) -> list[dict]:
    """Return ordered samples [{used_mb, ts}, ...] for sparkline rendering."""
```

**SQL:**
```sql
-- average
SELECT AVG(used_mb) FROM ram_samples WHERE ts >= ?
-- series (newest first, limited for rendering)
SELECT used_mb, ts FROM ram_samples WHERE ts >= ? ORDER BY ts DESC LIMIT ?
```

**Test:** `test_ram_aggregator.py` inserts synthetic rows, verifies averages.

---

## Phase 3 — Panel UI (`00_app/10_ram_window.py`)

**Functions:**
```python
def create_ram_panels() -> tuple[Gtk.Box, Gtk.Box, Gtk.Box]:
    """Return (panel_7d, panel_30d, panel_cluster).
    Cluster panel is hidden by default."""

def update_ram_panel(
    panel: Gtk.Box,
    title: str,
    value_mb: float | None,
    series: list[dict],
    seconds_ago: int,
) -> None:
    """Update the numeric label, trend strip, and footer of a panel."""
```

**Panel layout (each panel is a vertical `Gtk.Box`):**
- `Gtk.Label` — title ("7-Day Avg RAM")
- `Gtk.Label` — big value ("4.2 GB")
- `Gtk.DrawingArea` — trend strip (20 segments, proportional height)
- `Gtk.Label` — footer ("Updated 3s ago")

**Cluster panel variant:**
- Title: "CLUSTER RAM"
- Value: aggregated sum of peer used MB
- List of sub-labels per host with status dot (green = live, grey = stale >30s)
- Hidden by default; shown by `plugin.py` when loaded

**Test:** `test_ram_window.py` verifies widgets are created and `update_ram_panel` doesn't crash.

---

## Phase 4 — Window & Main Integration

### `window.py` — edit only

After the existing toggle button box, append the three panels:
```python
from _10_ram_window import create_ram_panels
# ... after box.append(overlay_btn) ...
panels = create_ram_panels()
for p in panels:
    box.append(p)
```

### `00_main.py` — edit only

After `win = create_window(app)`:
```python
from _08_ram_sampler import start_ram_sampler
from _09_ram_aggregator import get_average_ram, get_series
from _10_ram_window import update_ram_panel
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "04_data"
DB_PATH = DATA_DIR / "ram_data.db"

def _on_ram_sample(sample: dict, panels: tuple) -> None:
    """Schedule panel updates on GTK main thread."""
    GLib.idle_add(lambda: _refresh_panels(sample, panels))

def _refresh_panels(sample, panels):
    seven = get_average_ram(DB_PATH, 7)
    thirty = get_average_ram(DB_PATH, 30)
    series7 = get_series(DB_PATH, 7)
    series30 = get_series(DB_PATH, 30)
    update_ram_panel(panels[0], "7-Day Avg RAM", seven, series7, 0)
    update_ram_panel(panels[1], "30-Day Avg RAM", thirty, series30, 0)
    # panels[2] updated by plugin when loaded

t = start_ram_sampler(DB_PATH, lambda s: GLib.idle_add(_on_ram_sample, s, panels))
t.daemon = True
```

Also: load plugins after window creation, pass panels to plugin init.

---

## Phase 5 — Plugin System (`00_app/plugins/__init__.py`)

**Function:**
```python
def load_plugins(data_dir: Path, app: Gtk.Application) -> list[dict]:
    """Scan data_dir/plugins/*/index.py, validate contract, call init(), return list."""
```

**Contract per plugin (`index.py`):**
```python
def init(ctx: dict) -> dict:
    # ctx = {"app": Gtk.Application, "db_path": Path, "register_panel": callable}
    # register_panel(title, widget) adds widget to the main window
    # Returns: {"id": str, "name": str, "panel": Gtk.Widget}
```

**Loader logic:**
- Iterate `data_dir / "plugins"` for subdirectories
- Try `import plugin` from each; skip if `plugin.py` missing or `init` not callable
- Catch all exceptions, log to stderr, never crash
- Call `ctx["register_panel"](info["name"], info["panel"])` for each loaded plugin
- Return list of loaded plugin info dicts

---

## Phase 6 — CLUSTER Plugin (`00_app/plugins/cluster/`)

### `discover.py`

```python
def discover_cluster_roots(timeout: int = 5) -> list[dict]:
    """Send UDP broadcast probe to port 52052, collect root_announce replies.
    Returns [{"ip": str, "hostname": str, "http_port": int}, ...].
    Uses same UDP protocol as CLUSTER/src/common/discovery.py UDPBroadcastDiscovery."""
```

Protocol: send `{"type": "root_announce"}` broadcast; listen 3s for replies containing `"type": "root_announce"` with `hostname`, `port`, `http_port` fields.

### `connect.py`

```python
def fetch_root_ram_status(host: str, http_port: int = 8080, timeout: int = 3) -> dict | None:
    """GET http://{host}:{http_port}/api/status
    Parse JSON workers list, return {"hostname": str, "used_mb": float, "total_workers": int}
    or None on failure."""
```

Uses `urllib.request.urlopen` (stdlib). Parses `workers` array, sums `(ram_total - ram_available)` per worker.

### `plugin.py`

```python
def init(ctx: dict) -> dict:
    """Start discovery thread, poll roots every 10s, register cluster panel.
    Returns {"id": "cluster", "name": "CLUSTER", "panel": Gtk.Box}."""
```

Logic:
1. Create cluster panel via `panel.create_cluster_panel()`
2. Start background thread:
   - `roots = discover_cluster_roots()`
   - For each root: `status = fetch_root_ram_status(root["ip"], root["http_port"])`
   - Sum all `used_mb` values
   - Update panel with aggregated value and per-host breakdown
   - `time.sleep(10)`
3. On `register_panel("CLUSTER", panel)`, set panel visible
4. Return plugin info dict

### `panel.py`

```python
def create_cluster_panel() -> Gtk.Box:
    """Create the cluster RAM panel widget. Hidden by default."""
```

Layout:
- Title label "CLUSTER RAM"
- Aggregated used MB label (large)
- Per-host list labels ("hostname: 2.1 GB" with color indicator)
- Connection status footer

---

## Phase 7 — Tests

### `09_tests/test_ram_sampler.py`
- Mock `/proc/meminfo` via filesystem override
- Call `start_ram_sampler`, verify ≥1 row inserted after short sleep
- Verify WAL mode is enabled

### `09_tests/test_ram_aggregator.py`
- Create temp SQLite DB, insert known rows
- Assert `get_average_ram` returns correct mean
- Assert `get_series` returns rows in DESC order

### `09_tests/test_ram_window.py`
- Call `create_ram_panels()`, assert 3 panels returned
- Call `update_ram_panel` with sample data, assert labels updated
- Assert cluster panel is hidden initially

### `09_tests/test_cluster_plugin.py`
- Mock `urllib.request.urlopen` to return fake `/api/status` JSON
- Call `discover_cluster_roots` with mock socket
- Verify aggregation math and panel content

Run command:
```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=00_app pytest 09_tests/ -v
```

---

## Phase 8 — Commit & Push

```bash
git add .
git commit -m "feat: RAM monitor with 7d/30d averages and optional CLUSTER plugin"
git push -u origin feature/dashboard-ram-monitor
```

---

## Phase 9 — Documentation

### Update `README.md`

Add to `## Features`:
```markdown
### RAM Monitor
Two persistent windows showing average RAM usage:
- **7-Day Avg RAM**: Average used memory over the last 7 days (samples every 10s)
- **30-Day Avg RAM**: Average used memory over the last 30 days
- **CLUSTER RAM** (optional): When a CLUSTER root node is discovered on the network,
  an additional panel shows aggregated RAM from all connected workers.
  Enable via the CLUSTER plugin in `04_data/plugins/cluster/`.
```

Add to branch map table:
| `feature/dashboard-ram-monitor` | RAM monitor (7d/30d) + optional CLUSTER plugin | Active |

Add to `## Branch-Related File Changes`:
| File | Change |
|------|--------|
| `00_app/08_ram_sampler.py` | NEW — `/proc/meminfo` sampler, 10s interval, SQLite WAL persistence, 30-day purge |
| `00_app/09_ram_aggregator.py` | NEW — `get_average_ram(days)`, `get_series(days, limit)` SQL queries |
| `00_app/10_ram_window.py` | NEW — Panel factory: 7d, 30d, cluster panels with trend strips |
| `00_app/plugins/__init__.py` | NEW — Plugin loader: scans `04_data/plugins/`, validates contract, calls `init()` |
| `00_app/plugins/cluster/__init__.py` | NEW — Entry point delegating to `plugin.init()` |
| `00_app/plugins/cluster/plugin.py` | NEW — Discovery loop, HTTP polling of CLUSTER roots, panel registration |
| `00_app/plugins/cluster/discover.py` | NEW — UDP broadcast discovery of CLUSTER root nodes (port 52052) |
| `00_app/plugins/cluster/connect.py` | NEW — `fetch_root_ram_status()` via `/api/status` HTTP endpoint |
| `00_app/plugins/cluster/panel.py` | NEW — Cluster panel widget with per-host breakdown |
| `00_app/00_main.py` | EDITED — Starts RAM sampler and plugin loader on boot |
| `00_app/window.py` | EDITED — Appends 3 RAM panels below existing toggle button |
| `04_data/ram_data.db` | RUNTIME — SQLite DB, gitignored, created on first run |
| `09_tests/test_ram_sampler.py` | NEW |
| `09_tests/test_ram_aggregator.py` | NEW |
| `09_tests/test_ram_window.py` | NEW |
| `09_tests/test_cluster_plugin.py` | NEW |

---

## Definition of Done

- [ ] `python3 00_app/00_main.py` launches showing 3 RAM panels
- [ ] 7d/30d values are numerical averages from `/proc/meminfo` samples
- [ ] Trend strips render proportional bar charts
- [ ] Cluster panel is hidden when no CLUSTER plugin is loaded
- [ ] With CLUSTER root running: cluster panel shows aggregated peer RAM
- [ ] Dashboard runs identically without CLUSTER (2 RAM panels + toggle)
- [ ] All 4 new tests pass: `pytest 09_tests/ -v`
- [ ] `python3 -m py_compile 00_app/**/*.py` succeeds
- [ ] No absolute hardcoded paths
- [ ] Every new file has SPDX license header
- [ ] Feature branch pushed to remote
- [ ] README.md branch map and file change table updated

---

## Execution Order

```
0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
bootstrap → sampler → aggregator → panel UI → integration → plugin skeleton → cluster plugin → tests → commit → docs
```
