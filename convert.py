import csv
from datetime import datetime, timezone

with open('data.csv', 'r', encoding='utf-8') as infile, open('filter.txt', 'w', encoding='utf-8') as outfile:
    outfile.write('! ÖIAT Watchlist Internet - AdGuard Filter from CSV (https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/)\n')
    outfile.write(f'! Generated: {datetime.utcnow().isoformat()}Z\n')
    
    reader = csv.reader(infile, delimiter=';')
    next(reader, None)  # Skip Header
    
    for row in reader:
        if len(row) >= 1:
            domain = row[0].strip().strip('"')
            if not domain:
                print(f"Leere Domain: {row}")  # Debug-Ausgabe für leere Domains
            elif '.' in domain:
                outfile.write(f'||{domain}^|\n')
            else:
                print(f"Ungültige Domain: {domain}")  # Debug-Ausgabe für ungültige Domains
