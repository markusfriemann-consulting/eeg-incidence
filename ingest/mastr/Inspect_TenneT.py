import os, glob, sys

def detect_encoding(path: str) -> str:
    """Try encodings in priority order. Return the first that produces no mojibake."""
    candidates = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
    for enc in candidates:
        try:
            with open(path, encoding=enc) as f:
                sample = f.read(8000)
        except UnicodeDecodeError:
            continue
        # Mojibake signature: UTF-8 bytes read as cp1252/latin-1
        # If we see "Ã" followed by another character, that's likely a misread umlaut
        if 'Ã¼' in sample or 'Ã¤' in sample or 'Ã¶' in sample or 'ÃŸ' in sample or 'Ã©' in sample:
            continue  # try next encoding
        return enc
    return 'cp1252'  # last resort

paths = sorted(glob.glob('data_inbox/jahresabrechnung/extracted/*/*.csv'))

for path in paths:
    enc = detect_encoding(path)
    with open(path, encoding=enc) as f:
        first = f.readline().strip()
        second = f.readline().strip()
    print(f'\n--- {path} ---')
    print(f'  Encoding: {enc}')
    print(f'  Header:   {first[:300]}')
    print(f'  Sample:   {second[:300]}')