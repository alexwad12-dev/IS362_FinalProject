import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. Setup the list of years to scrape
# Range covers 2013-2023
years = range(2013, 2024)

# 2. Create a list to hold song data
all_songs = []

# 3. Define the User-Agent header to avoid 403 Forbidden errors
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("Starting Scrape...")

for year in years:
    url = f"https://www.billboard.com/charts/year-end/{year}/hot-100-songs/"
    print(f"Scraping {year}...")

    try:
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve {year}: Status {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        # Billboard's HTML structure relies on these specific classes.
        # Note: These class names are current as of late 2024 but may change.
        chart_items = soup.find_all("div", class_="o-chart-results-list-row-container")

        for item in chart_items:
            # Extract Rank
            rank_span = item.find("span", class_="c-label")
            rank = rank_span.get_text(strip=True) if rank_span else "N/A"

            # Extract Title (Usually inside an h3 tag with specific classes)
            title_h3 = item.find("h3", id="title-of-a-story")
            title = title_h3.get_text(strip=True) if title_h3 else "Unknown Title"

            # Extract Artist (Usually the span immediately after the title)
            # We look for the sibling span of the title container
            artist_span = title_h3.find_next_sibling("span", class_="c-label")
            artist = artist_span.get_text(strip=True) if artist_span else "Unknown Artist"

            # Append to our list
            all_songs.append({
                "Rank": rank,
                "Year": year,
                "Title": title,
                "Artist": artist
            })

        # Be polite to the server - Pause for 1 second between years.
        time.sleep(1)

    except Exception as e:
        print(f"Error scraping {year}: {e}")

# 4. Convert to DataFrame
df_billboard = pd.DataFrame(all_songs)

# 5. Clean up data
# Remove any non-numeric characters from Rank if necessary
df_billboard['Rank'] = pd.to_numeric(df_billboard['Rank'], errors='coerce')

# Check the results
print(f"Scraping complete. Found {len(df_billboard)} songs.")
print(df_billboard.head())

# 6. Save to CSV (Satisfies: reproducible data requirement)
df_billboard.to_csv("billboard_hot_100_2013_2023.csv", index=False)