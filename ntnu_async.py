import aiohttp
import asyncio
import ssl
import certifi
import math
import pandas as pd

BASE_URL = (
    "https://www.ntnu.edu/sok?"
    "p_p_id=ntnusearchpage_WAR_ntnusearchportlet&"
    "p_p_lifecycle=2&"
    "p_p_state=normal&"
    "p_p_mode=view&"
    "p_p_resource_id=search&"
    "p_p_cacheability=cacheLevelPage&"
    "query={query}&category=employee&sort=alpha&pageNr={page}"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# secure SSL (fixes SSLCertVerificationError on some Windows/Python setups)
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# limit concurrent requests to be polite and avoid throttling
MAX_CONCURRENCY = 10


async def fetch_json(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore, retries: int = 3):
    """GET URL and return parsed JSON with retries + backoff."""
    backoff = 1
    for attempt in range(1, retries + 1):
        try:
            async with sem:
                timeout = aiohttp.ClientTimeout(total=30)
                async with session.get(url, headers=HEADERS, ssl=SSL_CONTEXT, timeout=timeout) as resp:
                    if resp.status != 200:
                        raise aiohttp.ClientResponseError(
                            resp.request_info, resp.history, status=resp.status, message="Bad status"
                        )
                    # Some servers send "application/json; charset=utf-8"
                    return await resp.json(content_type=None)
        except Exception as e:
            if attempt == retries:
                print(f"❌ Giving up {url} after {retries} attempts. Last error: {e}")
                return None
            await asyncio.sleep(backoff)
            backoff *= 2  # exponential backoff


def extract_rows(docs):
    """Map NTNU JSON docs -> our row schema."""
    rows = []
    for d in docs or []:
        rows.append({
            "Name": d.get("title", "") or d.get("displayName", ""),
            "Email": (d.get("email") or "").strip(),
            "Position": d.get("roleTitle", "") or "",
            "Profile_URL": d.get("url", "") or "",
            "University": "NTNU",
        })
    return rows


async def scrape_letter(session: aiohttp.ClientSession, letter: str, sem: asyncio.Semaphore):
    """Scrape all pages for a single query letter using the JSON API."""
    all_rows = []

    # First page to learn total pages
    url1 = BASE_URL.format(query=letter, page=1)
    js = await fetch_json(session, url1, sem)
    if not js:
        return all_rows

    num_found = int(js.get("numFound", 0))
    page_size = int(js.get("pageSize", 10) or 10)
    total_pages = max(1, math.ceil(num_found / page_size))

    # page 1 docs
    all_rows.extend(extract_rows(js.get("docs", [])))

    # remaining pages
    if total_pages > 1:
        tasks = []
        for p in range(2, total_pages + 1):
            url = BASE_URL.format(query=letter, page=p)
            tasks.append(fetch_json(session, url, sem))
        pages = await asyncio.gather(*tasks)
        for js_page in pages:
            if js_page:
                all_rows.extend(extract_rows(js_page.get("docs", [])))

    print(f"✔ Letter '{letter}': pages={total_pages}, rows={len(all_rows)}")
    return all_rows


async def main():
    letters = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_letter(session, letter, sem) for letter in letters]
        results = await asyncio.gather(*tasks)

    # Flatten
    rows = [row for letter_rows in results for row in letter_rows]

    # Normalize and dedupe:
    df = pd.DataFrame(rows)
    if df.empty:
        print("No data scraped.")
        # Still write empty files for consistency
        df.to_csv("ntnu_employees.csv", index=False, encoding="utf-8-sig")
        df.to_excel("ntnu_employees.xlsx", index=False)
        return

    # Clean emails/urls for reliable dedupe
    df["Email"] = df["Email"].fillna("").str.strip().str.lower()
    df["Profile_URL"] = df["Profile_URL"].fillna("").str.strip()

    # Deduplicate:
    # 1) rows with email -> unique by Email
    # 2) rows without email -> unique by Profile_URL
    with_email = df[df["Email"] != ""].drop_duplicates(subset=["Email"])
    without_email = df[df["Email"] == ""].drop_duplicates(subset=["Profile_URL"])
    df_unique = pd.concat([with_email, without_email], ignore_index=True)

    # Optional: sort for readability
    df_unique = df_unique.sort_values(["Name", "Email"]).reset_index(drop=True)

    # Save
    df_unique.to_csv("ntnu_employees.csv", index=False, encoding="utf-8-sig")
    df_unique.to_excel("ntnu_employees.xlsx", index=False)

    print(f"✅ Scraped {len(df_unique)} unique employees across A–Z.")
    print("📂 Files written: 'ntnu_employees.csv', 'ntnu_employees.xlsx'.")


if __name__ == "__main__":
    asyncio.run(main())
