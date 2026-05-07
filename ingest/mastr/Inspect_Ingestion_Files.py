import csv

PATH = 'extracted/transnetbw/TransnetBW_2024_EEGZahlungen_Bewegungsdaten_Teil1.csv'

counts = {'monthly': 0, 'annual': 0, 'empty': 0, 'other': 0}
sample_anlagen = {}

with open(PATH, encoding='cp1252') as f:
    reader = csv.DictReader(f, delimiter=';')
    for i, row in enumerate(reader):
        if i >= 100_000:
            break
        m = row['Monat'].strip()
        if m == '':
            counts['empty'] += 1
        elif m == '0':
            counts['annual'] += 1
        elif m in {str(x) for x in range(1, 13)}:
            counts['monthly'] += 1
        else:
            counts['other'] += 1

        anlage = row['EEG_Mastr_Nr']
        if len(sample_anlagen) < 5 or anlage in sample_anlagen:
            sample_anlagen.setdefault(anlage, []).append(
                (m, row['Veraeusserungsform'], row['EEG_Zahlung'])
            )

print('Monat distribution in first 100k rows:')
for k, v in counts.items():
    print(f'  {k}: {v:,}')

print('\nSample Anlagen and their entry patterns:')
for anlage, entries in list(sample_anlagen.items())[:5]:
    print(f'\n  {anlage}: {len(entries)} entries')
    for monat, form, zahlung in entries[:15]:
        print(f'    Monat={monat or "(empty)"}, Form={form}, Zahlung={zahlung}')