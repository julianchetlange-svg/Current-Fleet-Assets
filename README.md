# Current Fleet Assets

Daily McCoy's fleet asset report, built from the Fexa "Daily Fleet Asset Report" email.

- `index.html` – the report. Self-contained (page, runtime and data in one file), so it works from GitHub Pages or any static host.
- `assets.json` – the asset rows behind the report.
- `report_page.html` – the page source (also used by the claude.ai version of the report).
- `Asset_Class_Key.xlsx` – asset template name -> asset class. Add new templates here.
- `build_rows.py` – Fexa `.xls` + Asset Class Key `.xlsx` -> `assets.json`.
  `python3 build_rows.py report.xls class_key.xlsx assets.json [YYYY-MM-DD]`
- `build_changes.py` – compares the previous `assets.json` with the new one and keeps a 31-day history in `change_runs.json` and `change_events.json` (the report's Changes tab).
  `python3 build_changes.py old_assets.json assets.json change_runs.json change_events.json YYYY-MM-DD`
- `build_standalone.py` – `report_page.html` + data -> `index.html`.
  `python3 build_standalone.py report_page.html assets.json index.html change_runs=change_runs.json change_events=change_events.json`

Rules applied in `build_rows.py`:
- Asset class comes from the asset class key, matched on Asset Template Name. Unmatched templates show as "Unmapped".
- "033/355 Multi-Department" (including "033/355 Multi-Department, Region 05") is reported as Region 05.
- A blank district on a "Region N" store is reported as Region 0N.
- Age is whole months from Asset Date of Origination to the report date.
