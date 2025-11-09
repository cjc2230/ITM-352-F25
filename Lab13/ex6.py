# ...existing code...
import re, requests
from bs4 import BeautifulSoup as BS

s = requests.get("https://www.hicentral.com/hawaii-mortgage-rates.php", timeout=10).text
soup = BS(s, "html.parser")
for table in soup.find_all("table"):
    out = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"]) if c.get_text(strip=True)]
        if cells:
            rates = re.findall(r"\d+\.\d+%?", " ".join(cells[1:]))
            if rates:
                out.append(f"{cells[0]} -> {', '.join(rates)}")
    if out:
        print("\n".join(out))
        break
