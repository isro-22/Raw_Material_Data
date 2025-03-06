## Version 0.0 (01 March 2025)
# Scrap data from thegoodscents without class

## Version 1.0 (03 March 2025)
# Converting Old code to make class mode
# Including Odor Descriptor and Odor Type

## Version 2.0 (06 March 2025)
# Added solubility data scrap
# Processing 20 links per batch
# Saving temporary results in files named scraped_data-{i}.csv
# Merging all scraped_data-{i}.csv files into a single file scraped_data_final.csv

import requests
from bs4 import BeautifulSoup
import csv
import re
import os


class GoodScentsScraper:
    def __init__(self, urls):
        self.urls = urls
        self.data = []

    def scrape_page(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Gagal mengakses {url}, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('span', itemprop='name').get_text(strip=True) if soup.find('span',
                                                                                    itemprop='name') else "Tidak ditemukan"
        head_synonym = soup.find('span', class_='headsynonym').get_text(strip=True) if soup.find('span',
                                                                                                 class_='headsynonym') else "Tidak ditemukan"

        compound_name = cas_number = molecular_weight = formula = "Tidak ditemukan"
        table = soup.find('table', class_='cheminfo')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label, value = cells[0].get_text(strip=True), cells[1].get_text(strip=True)
                    if "Name:" in label:
                        compound_name = value
                    elif "CAS Number:" in label:
                        cas_number = value
                    elif "Molecular Weight:" in label:
                        molecular_weight = value
                    elif "Formula:" in label:
                        formula = value

        appearance = assay = specific_gravity = refractive_index = melting_point = boiling_point = flash_point = "Tidak ditemukan"
        physical_table = soup.find_all('table', class_='cheminfo')
        for table in physical_table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label, value = cells[0].get_text(strip=True), cells[1].get_text(strip=True)
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
                        boiling_point = value if boiling_point == "Tidak ditemukan" else f"{boiling_point}, {value}"
                    elif "Flash Point:" in label:
                        flash_point = value

        odor_type, odor_strength = self.scrape_organoleptic(soup)

        solubility_scraper = SolubilityScraper()
        soluble_in = solubility_scraper.extract_data(soup, "Soluble in")
        insoluble_in = solubility_scraper.extract_data(soup, "Insoluble in")

        print(f"{url} telah berhasil di-scrap.")
        return [url, name, head_synonym, compound_name, cas_number, molecular_weight, formula, appearance, assay,
                specific_gravity, refractive_index, melting_point, boiling_point, flash_point, odor_type, odor_strength,
                soluble_in, insoluble_in]

    def scrape_organoleptic(self, soup):
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

        return odor_type, odor_strength

    def scrape(self):
        for url in self.urls:
            data = self.scrape_page(url)
            if data:
                self.data.append(data)


class OdorScraper:
    def __init__(self, urls):
        self.urls = urls
        self.data = {}

    def scrape(self):
        for url in self.urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for td in soup.find_all("td", class_="radw5"):
                        if "Odor Description:" in td.get_text():
                            spans = td.find_all("span")
                            if len(spans) >= 2:
                                threshold = spans[0].get_text(strip=True)
                                span_texts = spans[1].get_text("\n", strip=True).split("\n")
                                description = span_texts[0].strip() if len(span_texts) > 0 else ""
                                source = " ".join(span_texts[1:]).strip() if len(span_texts) > 1 else ""
                                self.data[url] = [threshold, description, source]
                            break
                print(f"{url} telah berhasil di-scrap untuk data odor.")
            except Exception as e:
                print(f"Error scraping {url}: {e}")


class SolubilityScraper:
    @staticmethod
    def extract_data(soup, section_text):
        items = []
        section = soup.find("td", class_="synonyms", string=re.compile(section_text, re.I))

        if section:
            tr = section.find_parent("tr")
            for sibling in tr.find_next_siblings("tr"):
                td = sibling.find("td", class_=re.compile("wrd"))
                if td:
                    items.append(td.text.strip())
                else:
                    break

        return "; ".join(items) if items else "Tidak ditemukan"


if __name__ == "__main__":
    input_file = "/Input/list.txt"

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error membaca file teks: {e}")
        exit()

    batch_size = 20
    num_batches = (len(urls) + batch_size - 1) // batch_size  # Hitung jumlah batch

    for i in range(num_batches):
        batch_urls = urls[i * batch_size: (i + 1) * batch_size]
        output_file = f"scraped_data-{i + 1}.csv"

        scraper = GoodScentsScraper(batch_urls)
        scraper.scrape()

        odor_scraper = OdorScraper(batch_urls)
        odor_scraper.scrape()

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["URL", "Name", "Head Synonym", "Compound Name", "CAS Number", "Molecular Weight", "Formula",
                 "Appearance",
                 "Assay", "Specific Gravity", "Refractive Index", "Melting Point", "Boiling Point", "Flash Point",
                 "Odor Type", "Odor Strength", "Threshold", "Description", "Source", "Soluble In", "Insoluble In"])

            for data in scraper.data:
                url = data[0]
                odor_data = odor_scraper.data.get(url, ["Tidak ditemukan"] * 3)
                writer.writerow(data[:16] + odor_data + data[16:])

        print(f"Batch {i + 1} selesai, data disimpan dalam {output_file}")

    print("Semua batch selesai. Sekarang menggabungkan semua file CSV...")
    with open("scraped_data_final.csv", "w", newline="", encoding="utf-8") as final_csv:
        writer = csv.writer(final_csv)
        writer.writerow(
            ["URL", "Name", "Head Synonym", "Compound Name", "CAS Number", "Molecular Weight", "Formula", "Appearance",
             "Assay", "Specific Gravity", "Refractive Index", "Melting Point", "Boiling Point", "Flash Point",
             "Odor Type", "Odor Strength", "Threshold", "Description", "Source", "Soluble In", "Insoluble In"])

        for i in range(num_batches):
            with open(f"scraped_data-{i + 1}.csv", "r", encoding="utf-8") as batch_csv:
                next(batch_csv)
                for line in batch_csv:
                    final_csv.write(line)

    print("Semua data telah digabung dalam scraped_data_final.csv ✅")

