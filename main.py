import requests
from bs4 import BeautifulSoup
import csv

# Baca daftar URL dari file teks
input_file = "Input/link.txt"
output_file = "Output/scraped_data.csv"

urls = []
try:
    with open(input_file, "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]
except Exception as e:
    print(f"Error membaca file teks: {e}")
    exit()

# Buka file output untuk menyimpan hasil
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ["URL", "Name", "Head Synonym", "Compound Name", "CAS Number", "Molecular Weight", "Formula", "Appearance",
         "Assay", "Specific Gravity", "Refractive Index", "Melting Point", "Boiling Point", "Flash Point", "Odor Type",
         "Odor Strength"])

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                name = soup.find('span', itemprop='name').get_text(strip=True) if soup.find('span',
                                                                                            itemprop='name') else "Tidak ditemukan"
                head_synonym = soup.find('span', class_='headsynonym').get_text(strip=True) if soup.find('span',
                                                                                                         class_='headsynonym') else "Tidak ditemukan"

                compound_name = cas_number = molecular_weight = formula = "Tidak ditemukan"
                for row in soup.select('table.cheminfo tr'):
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

                appearance = assay = specific_gravity = refractive_index = melting_point = boiling_point = flash_point = "Tidak ditemukan"
                for row in soup.select('table.cheminfo tr'):
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

                odor_type = odor_strength = "Tidak ditemukan"
                for row in soup.select('table.cheminfo tr'):
                    cells = row.find_all('td')
                    if len(cells) == 1:
                        text = cells[0].get_text(strip=True)
                        if "Odor Type:" in text:
                            odor_type = text.split(":", 1)[-1].strip()
                        elif "Odor Strength:" in text:
                            odor_strength = text.split(":", 1)[-1].strip()

                writer.writerow(
                    [url, name, head_synonym, compound_name, cas_number, molecular_weight, formula, appearance, assay,
                     specific_gravity, refractive_index, melting_point, boiling_point, flash_point, odor_type,
                     odor_strength])
                print(f"Data untuk {url} telah disimpan.")
            else:
                print(f"Gagal mengakses {url}, status code: {response.status_code}")
        except Exception as e:
            print(f"Error saat mengakses {url}: {e}")

print(f"Scraping selesai. Data disimpan dalam {output_file}")