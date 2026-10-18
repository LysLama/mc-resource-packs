with open(r'E:\ModrinthApp\profiles\Fabric 26.3\logs\latest.log', 'r', encoding='utf-8', errors='ignore') as f:
    capture = False
    for line in f:
        if '[11:41:17]' in line:
            capture = True
        if '[11:42:02]' in line:
            capture = False
        if capture:
            if any(term in line for term in ['EMF', 'ETF', 'optifine', 'cem', 'cow', 'model', 'Exception', 'Error', 'WARN']):
                print(line.strip()[:140])
