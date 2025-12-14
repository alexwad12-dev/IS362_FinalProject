import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# 1. SETUP: Authenticate with Spotify
# Replace these with your actual keys from the dashboard!
cid = ''
secret = ''

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# 2. LOAD DATA: Load the CSV data
# (Verify filepath is correct)
df = pd.read_csv("../billboard_hot_100_2013_2023.csv")


# 3. DEFINE THE FUNCTION
def get_spotify_data(row):
    title = row['Title']
    artist = row['Artist']

    # Cleaning the artist name slightly helps search accuracy
    # (e.g., changing "Drake Featuring Future" to just "Drake")
    search_artist = artist.split(' Featuring')[0].split(' &')[0]

    # Construct a search query (q='track:X artist:Y')
    query = f"track:{title} artist:{search_artist}"

    try:
        # Step A: Search for the song
        result = sp.search(q=query, type='track', limit=1)

        # Check if anything was found
        if len(result['tracks']['items']) == 0:
            return pd.Series([None, None, None, None])

        # Get the Spotify ID of the top result
        track = result['tracks']['items'][0]
        track_id = track['id']

        # Step B: Get Audio Features using the ID
        features = sp.audio_features(track_id)[0]

        # Return the specific metrics you want for your project
        if features:
            return pd.Series([
                features['valence'],
                features['energy'],
                features['mode'],
                track_id
            ])
        else:
            return pd.Series([None, None, None, None])

    except Exception as e:
        print(f"Error processing {title}: {e}")
        return pd.Series([None, None, None, None])


# 4. RUN THE PROCESS
print("Starting Spotify API calls... this may take a few minutes.")

# We apply the function to every row in the dataframe.
# This creates new columns for our data.
df[['Valence', 'Energy', 'Mode', 'Spotify_ID']] = df.apply(get_spotify_data, axis=1)

# 5. CHECK & SAVE
# Let's see how many nulls we have (songs that weren't found)
print(f"Number of songs not found: {df['Valence'].isna().sum()}")

# Drop rows where we couldn't find the song (Optional, helps clean up data)
df_clean = df.dropna(subset=['Valence'])

# Save to a new CSV so we don't have to run the API again!
df_clean.to_csv("billboard_with_spotify_data.csv", index=False)

print("Done! Data saved to 'billboard_with_spotify_data.csv'")