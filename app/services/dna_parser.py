import csv
from io import TextIOWrapper, BytesIO
from zipfile import ZipFile
from app.models.upload import DNASNP

def parse_dna(bytes_content: bytes, filename: str) -> list[dict]:
    snps = []
    file_obj = BytesIO(bytes_content)

    if filename.lower().endswith('.zip'):
        with ZipFile(file_obj) as z:
            txt_name = next((f for f in z.namelist() if f.lower().endswith('.txt')), None)
            if not txt_name:
                raise ValueError("No .txt in zip")
            file_obj = z.open(txt_name)

    reader = csv.reader(TextIOWrapper(file_obj, encoding='utf-8', errors='ignore'), dialect='excel-tab')

    headers = None
    for row in reader:
        if not row or row[0].startswith('#'):
            continue
        if row[0].lower().startswith('rsid'):
            headers = [h.strip().lower() for h in row]
            continue
        if headers and len(row) >= 4:
            rsid, chrom, pos = row[0:3]
            if 'allele1' in headers and 'allele2' in headers:
                a1 = row[headers.index('allele1')]
                a2 = row[headers.index('allele2')]
                genotype = (a1 + a2).replace('0', '--').upper()
            elif 'genotype' in headers:
                genotype = row[headers.index('genotype')].upper()
            else:
                continue

            chrom = chrom.upper()
            if chrom == 'X': chrom = '23'
            if chrom == 'Y': chrom = '24'
            if chrom == 'MT': chrom = '26'

            snps.append({
                "rsid": rsid,
                "chromosome": chrom,
                "position": pos,
                "genotype": genotype
            })

    return snps