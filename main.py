## Version 1.0
# Converting Old code to make class mode
# Including Odor Descriptor and Odor Type



import requests
from bs4 import BeautifulSoup
import csv


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

        print(f"{url} telah berhasil di-scrap.")
        return [url, name, head_synonym, compound_name, cas_number, molecular_weight, formula, appearance, assay,
                specific_gravity, refractive_index, melting_point, boiling_point, flash_point, odor_type, odor_strength]

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


if __name__ == "__main__":
    input_file = "link.txt"
    output_file = "scraped_data.csv"

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error membaca file teks: {e}")
        exit()

    scraper = GoodScentsScraper(urls)
    scraper.scrape()

    odor_scraper = OdorScraper(urls)
    odor_scraper.scrape()

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["URL", "Name", "Head Synonym", "Compound Name", "CAS Number", "Molecular Weight", "Formula", "Appearance",
             "Assay", "Specific Gravity", "Refractive Index", "Melting Point", "Boiling Point", "Flash Point",
             "Odor Type", "Odor Strength", "Threshold", "Description", "Source"])

        for data in scraper.data:
            url = data[0]
            odor_data = odor_scraper.data.get(url, ["Tidak ditemukan"] * 3)
            writer.writerow(data + odor_data)

    print(f"Data telah disimpan dalam {output_file}")
