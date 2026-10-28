# Current Fleet Assets

Source for the McCoy's daily fleet asset report (built from the Fexa "Daily Fleet Asset Report" email).

- `index.html` – the report page (filters, class/region breakdowns, grouped asset list). It reads a dataset named `assets`.
- `build_rows.py` – turns the Fexa `.xls` plus the Asset Class Key `.xlsx` into the `assets` rows (JSON).
  Usage: `python3 build_rows.py report.xls class_key.xlsx assets.json [YYYY-MM-DD]`

Rules applied in `build_rows.py`:
- Asset class comes from the asset class key, matched on Asset Template Name. Unmatched templates show as "Unmapped".
- "033/355 Multi-Department" (including "033/355 Multi-Department, Region 05") is reported as Region 05.
- A blank district on a "Region N" store is reported as Region 0N.
- Age is whole months from Asset Date of Origination to the report date.

The asset data itself (serial numbers, store assignments) is not stored in this public repository.
