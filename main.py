import requests
from bs4 import BeautifulSoup
import csv

# URL yang ingin di-scrap
url = "https://www.thegoodscentscompany.com/data/rw1056361.html"

# Mengirim permintaan GET ke halaman
response = requests.get(url)

# Pastikan permintaan berhasil
if response.status_code == 200:
    # Parsing HTML menggunakan BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Simpan seluruh HTML halaman dalam file txt
    with open("scraped_page.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print("HTML halaman telah disimpan dalam scraped_page.html")

    # Mengambil name dan head synonym
    name = soup.find('span', itemprop='name').get_text(strip=True) if soup.find('span',
                                                                                itemprop='name') else "Tidak ditemukan"
    head_synonym = soup.find('span', class_='headsynonym').get_text(strip=True) if soup.find('span',
                                                                                             class_='headsynonym') else "Tidak ditemukan"

    # Mengambil informasi dari tabel cheminfo
    table = soup.find('table', class_='cheminfo')
    compound_name = cas_number = molecular_weight = formula = "Tidak ditemukan"

    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)

                if "Name:" in label:
                    compound_name = value
                elif "CAS Number:" in label:
                    cas_number = value
                elif "Molecular Weight:" in label:
                    molecular_weight = value
                elif "Formula:" in label:
                    formula = value

    # Mengambil informasi dari tabel Physical Properties
    physical_table = soup.find_all('table', class_='cheminfo')
    appearance = assay = specific_gravity = refractive_index = melting_point = boiling_point = flash_point = "Tidak ditemukan"

    for table in physical_table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)

                if "Appearance:" in label:
                    appearance = value
                elif "Assay:" in label:
                    assay = value
                elif "Specific Gravity:" in label:
                    specific_gravity = value
                elif "Refractive Index:" in label:
                    refractive_index = value
                elif "Melting Point:" in label:
                    melting_point = value
                elif "Boiling Point:" in label:
                    if boiling_point == "Tidak ditemukan":
                        boiling_point = value
                    else:
                        boiling_point += ", " + value
                elif "Flash Point:" in label:
                    flash_point = value

    # Mengambil informasi dari tabel Organoleptic Properties
    odor_type = odor_strength = "Tidak ditemukan"
    organoleptic_table = soup.find_all('table', class_='cheminfo')

    for table in organoleptic_table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 1:
                text = cells[0].get_text(strip=True)
                if "Odor Type:" in text:
                    odor_type = text.split(":", 1)[-1].strip()
                elif "Odor Strength:" in text:
                    odor_strength = text.split(":", 1)[-1].strip()

    # Simpan dalam file CSV
    with open("scraped_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Name", "Head Synonym", "Compound Name", "CAS Number", "Molecular Weight", "Formula", "Appearance",
             "Assay", "Specific Gravity", "Refractive Index", "Melting Point", "Boiling Point", "Flash Point",
             "Odor Type", "Odor Strength"])
        writer.writerow([name, head_synonym, compound_name, cas_number, molecular_weight, formula, appearance, assay,
                         specific_gravity, refractive_index, melting_point, boiling_point, flash_point, odor_type,
                         odor_strength])

    print("Data telah disimpan dalam scraped_data.csv")
else:
    print(f"Gagal mengakses halaman, status code: {response.status_code}")