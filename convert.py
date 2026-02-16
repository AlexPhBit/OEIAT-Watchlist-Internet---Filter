import csv
from datetime import datetime, timezone

with open('data.csv', 'r', encoding='utf-8') as infile, open('filter.txt', 'w', encoding='utf-8') as outfile:
    outfile.write('! ÖIAT Watchlist Internet - AdGuard Filter from CSV (https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/)\n')
    outfile.write(f'! Generated: {datetime.now(timezone.utc).isoformat()}Z\n')
    
    reader = csv.reader(infile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    next(reader, None)  # Skip Header
    
    for i, row in enumerate(reader, start=2):  # Zeilennummer für Debug
        if len(row) >= 1 and row[0].strip():  # Prüfe non-empty
            domain = row[0].strip().strip('"')
            if domain and '.' in domain and len(domain) > 1:
                outfile.write(f'{domain}\n')
            else:
                print(f"Zeile {i}: Ungültige Domain '{row[0]}' übersprungen")
        else:
            print(f"Zeile {i}: Leere oder unvollständige Row '{row}' übersprungen")
