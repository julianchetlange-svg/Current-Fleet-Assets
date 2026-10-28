"""Track changes between two daily reports and keep a rolling 31-day history.
usage: build_changes.py old_assets.json new_assets.json change_runs.json change_events.json YYYY-MM-DD
old_assets.json may be missing (first run = baseline).  Re-running for a report date that is already in
change_runs.json leaves the history untouched."""
import sys, os, json, datetime as dt

old_f, new_f, runs_f, ev_f, run_date = sys.argv[1:6]
KEEP_DAYS = 31
new = {r['asset_number']: r for r in json.load(open(new_f))}
runs = json.load(open(runs_f)) if os.path.exists(runs_f) else []
events = json.load(open(ev_f)) if os.path.exists(ev_f) else []

if any(r['date'] == run_date for r in runs):
    print('already recorded for', run_date, '- history unchanged'); sys.exit(0)

def store_label(r): return r['store']
ev = []
def add(kind, r, detail):
    ev.append({'event_id': f"{run_date}|{r['asset_number']}|{kind}|{len(ev)}", 'date': run_date, 'change_type': kind,
               'asset_number': r['asset_number'], 'asset_class': r['asset_class'], 'asset_name': r['asset_name'],
               'store': r['store'], 'region': r['region'], 'detail': detail})

baseline = not os.path.exists(old_f)
if not baseline:
    old = {r['asset_number']: r for r in json.load(open(old_f))}
    for k, r in new.items():
        if k not in old:
            add('Added', r, f"New asset at {r['store']}")
    for k, r in old.items():
        if k not in new:
            add('Removed', r, f"No longer in the report (was at {r['store']})")
    for k, n in new.items():
        o = old.get(k)
        if not o: continue
        if o['store_number'] != n['store_number']:
            add('Transferred', n, f"Store: {o['store']} → {n['store']}")
        for f, lab in (('status', 'Status'), ('ownership', 'Ownership')):
            if o[f] != n[f]: add('Status', n, f"{lab}: {o[f]} → {n[f]}")
        for f, lab in (('asset_name', 'Template'), ('manufacturer', 'Manufacturer'), ('serial_number', 'Serial number'), ('in_service_date', 'In-service date')):
            if o[f] != n[f]: add('Other', n, f"{lab}: {o[f] or 'blank'} → {n[f] or 'blank'}")

cnt = lambda t: sum(1 for e in ev if e['change_type'] == t)
runs.append({'date': run_date, 'assets': len(new), 'added': cnt('Added'), 'removed': cnt('Removed'), 'transferred': cnt('Transferred'),
             'status': cnt('Status'), 'other': cnt('Other'), 'baseline': baseline})
events += ev
cut = (dt.date.fromisoformat(run_date) - dt.timedelta(days=KEEP_DAYS)).isoformat()
runs = sorted([r for r in runs if r['date'] > cut], key=lambda r: r['date'])
events = sorted([e for e in events if e['date'] > cut], key=lambda e: (e['date'], e['asset_number']))
json.dump(runs, open(runs_f, 'w'), separators=(',', ':')); json.dump(events, open(ev_f, 'w'), separators=(',', ':'))
print(run_date, 'baseline' if baseline else '', {k: cnt(k) for k in ('Added','Removed','Transferred','Status','Other')}, '| runs', len(runs), 'events', len(events))
