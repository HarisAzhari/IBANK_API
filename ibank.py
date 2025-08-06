import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin


class IBANScraper:
    def __init__(self):
        self.base_url = "https://bank-code.net"
        self.session = requests.Session()
        # Ultra stealth headers to bypass all detection
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.google.com/search?q=iban+checker",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def scrape_iban_info(self, iban):
        """
        Scrape IBAN information from bank-code.net
        """
        url = f"{self.base_url}/iban-checker?iban={iban}"

        try:
            print(f"🔍 Scraping IBAN info for: {iban}")
            print(f"📡 URL: {url}")

            # Add delay to seem more human-like
            time.sleep(2)

            response = self.session.get(url, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")

            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            print(f"🔍 Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"🔍 Page content length: {len(response.content)} bytes")

            # Extract data from the table
            data = {}

            # Debug: Print all tables found
            all_tables = soup.find_all("table")
            print(f"🔍 Total tables found: {len(all_tables)}")
            for i, table in enumerate(all_tables):
                print(f"   Table {i}: class={table.get('class', 'No class')}")
                print(f"   Table {i}: rows={len(table.find_all('tr'))}")
                if table.find_all("tr"):
                    first_row_text = table.find_all("tr")[0].get_text(strip=True)[:100]
                    print(f"   Table {i}: first row preview: {first_row_text}...")

            if not all_tables:
                print("😱 No tables found on the page!")
                print(f"🔍 Page content preview: {soup.get_text()[:300]}...")
                return None

            # Look for the table with Swift/BIC code information
            tables = soup.find_all("table", class_="table")

            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        header = cells[0].get_text(strip=True)
                        value_cell = cells[1]

                        # Extract Swift/BIC code
                        if "Swift" in header or "BIC" in header:
                            # Look for link in the cell
                            link = value_cell.find("a")
                            if link:
                                swift_code = link.get_text(strip=True)
                                swift_url = link.get("href", "")
                                if swift_url.startswith("//"):
                                    swift_url = "https:" + swift_url
                                elif swift_url.startswith("/"):
                                    swift_url = urljoin(self.base_url, swift_url)

                                data["swift_bic_code"] = swift_code
                                data["swift_url"] = swift_url
                            else:
                                data["swift_bic_code"] = value_cell.get_text(strip=True)

                        # Extract other information
                        elif "Bank" in header and "code" not in header.lower():
                            data["bank_name"] = value_cell.get_text(strip=True)
                        elif "Country" in header:
                            data["country"] = value_cell.get_text(strip=True)
                        elif "City" in header:
                            data["city"] = value_cell.get_text(strip=True)
                        elif "Branch" in header:
                            data["branch"] = value_cell.get_text(strip=True)
                        elif "Address" in header:
                            data["address"] = value_cell.get_text(strip=True)

            # Add IBAN to the data
            data["iban"] = iban
            data["scraped_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

            return data

        except requests.RequestException as e:
            print(f"❌ Error scraping {url}: {e}")
            print(
                f"💥 Response status code: {getattr(e.response, 'status_code', 'Unknown')}"
            )
            print(
                f"💥 Response text: {getattr(e.response, 'text', 'No response text')[:200]}..."
            )
            return None
        except Exception as e:
            print(f"❌ Parsing error: {e}")
            print(f"💥 Exception type: {type(e).__name__}")
            return None

    def save_data(self, data, filename="iban_data.json"):
        """
        Save scraped data to JSON file
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to {filename}")


def main():
    # Example usage
    iban = "RO75RZBR0000060007010397"

    scraper = IBANScraper()

    print("🚀 Starting IBAN scraping...")
    print("=" * 50)

    # Scrape the IBAN information
    data = scraper.scrape_iban_info(iban)

    if data:
        print("\n✨ Scraped Data:")
        print("=" * 30)
        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        # Save to file
        scraper.save_data(data)

        print(
            f"\n💫 Successfully scraped Swift/BIC code: {data.get('swift_bic_code', 'N/A')}"
        )
    else:
        print("💔 Failed to scrape data")


if __name__ == "__main__":
    main()
