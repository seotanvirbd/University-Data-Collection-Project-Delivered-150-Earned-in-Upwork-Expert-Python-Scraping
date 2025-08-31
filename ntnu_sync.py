import requests
import pandas as pd
import time

BASE_URL = "https://www.ntnu.edu/sok?p_p_id=ntnusearchpage_WAR_ntnusearchportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=search&p_p_cacheability=cacheLevelPage&query=ab&category=employee&sort=alpha&pageNr={}"

def scrape_ntnu():
    data = []
    page = 1
    total = None

    while True:
        print(f"Scraping page {page}...")
        url = BASE_URL.format(page)

        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed on page {page}: {e}")
            time.sleep(5)  # wait a bit before retry
            continue  # skip to next iteration

        js = resp.json()

        # figure out how many pages exist
        if total is None:
            num_found = js.get("numFound", 0)
            page_size = js.get("pageSize", 10)
            total = (num_found // page_size) + (1 if num_found % page_size else 0)
            print(f"Total employees: {num_found}, Pages: {total}")

        docs = js.get("docs", [])
        if not docs:
            break

        for d in docs:
            data.append({
                "Name": d.get("title", ""),
                "Email": d.get("email", ""),
                "Position": d.get("roleTitle", ""),
                "Profile_URL": d.get("url", ""),
                "University": "NTNU"
            })

        if page >= total:
            break

        page += 1
        time.sleep(1)  # small delay to avoid hitting server too hard

    # save to CSV + Excel
    df = pd.DataFrame(data)
    df.to_csv("ntnu_employees.csv", index=False, encoding="utf-8-sig")
    df.to_excel("ntnu_employees.xlsx", index=False)
    print("✅ Done! Data saved to ntnu_employees.csv and ntnu_employees.xlsx")

if __name__ == "__main__":
    scrape_ntnu()
