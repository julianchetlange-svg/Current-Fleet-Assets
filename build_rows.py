"""Fexa Daily Fleet Asset Report (.xls) + Asset Class Key (.xlsx) -> rows.json
usage: build_rows.py report.xls class_key.xlsx out.json [YYYY-MM-DD run date]"""
import sys, json, datetime as dt
import pandas as pd, openpyxl

report, keyf, out = sys.argv[1:4]
run = dt.date.fromisoformat(sys.argv[4]) if len(sys.argv) > 4 else dt.date.today()

key = {str(r[0]).strip(): str(r[1]).strip()
       for r in openpyxl.load_workbook(keyf).active.iter_rows(min_row=1, values_only=True)
       if r[0] and r[1] and str(r[0]).strip() != 'Asset Template Name'}

df = pd.read_excel(report, dtype=str).fillna('')
df = df.apply(lambda c: c.str.strip())

def region(district, store_name):
    d = district
    if d.startswith('033/355 Multi-Department'):
        return 'Region 05'
    if d == '':
        # blank district: the "Region N" store rows (e.g. store "Region 2") -> Region 0N
        import re
        m = re.fullmatch(r'Region (\d)', store_name)
        return f'Region 0{m.group(1)}' if m else 'Unassigned'
    return d

def months(d0, d1):
    return (d1.year - d0.year) * 12 + (d1.month - d0.month) - (1 if d1.day < d0.day else 0)

rows, unmapped, bad = [], set(), 0
for _, r in df.iterrows():
    tpl = r['Asset Template Name']
    cls = key.get(tpl)
    if cls is None:
        unmapped.add(tpl); cls = 'Unmapped'
    d0 = pd.to_datetime(r['Asset Date of Origination'], errors='coerce')
    if pd.isna(d0):
        bad += 1; age = None; ins = ''
    else:
        age = max(0, months(d0.date(), run)); ins = d0.date().isoformat()
    rows.append({
        'report_date': run.isoformat(),
        'region': region(r['Store District'], r['Store Name']),
        'store_number': r['Store Number'],
        'store_name': r['Store Name'],
        'store': f"{r['Store Number']} {r['Store Name']}",
        'asset_class': cls,
        'asset_name': tpl,
        'asset_number': r['Asset Name'],
        'manufacturer': r['Asset Manufacturer Name'] or 'Unknown',
        'serial_number': r['Asset Serial Number'],
        'ownership': r['Asset Ownership'],
        'status': r['Asset Status'],
        'in_service_date': ins,
        'age_months': age,
    })
json.dump(rows, open(out, 'w'), separators=(',', ':'))
print(len(rows), 'rows; unmapped templates:', sorted(unmapped), '; bad dates:', bad)
