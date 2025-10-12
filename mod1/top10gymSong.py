import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import csv
import time

# Authenticate
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

# Playlists for different sports
playlists = {
    "gym": "61ffYFj8I4jMQeSE4SZWKF",   # Replace with real playlist IDs
    "running": "37i9dQZF1DXdxcBWuJkbcy"
}

all_data = []

for sport, playlist_id in playlists.items():
    print(f"Fetching playlist for: {sport}")
    results = sp.playlist_tracks(playlist_id, limit=50)
    
    sport_data = {
        "sport": sport,
        "playlist_id": playlist_id,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "songs": []
    }
    
    for item in results['items']:
        track = item['track']
        if track:
            sport_data["songs"].append({
                "song": track['name'],
                "artist": ", ".join([a['name'] for a in track['artists']]),
                "album": track['album']['name'],
                "url": track['external_urls']['spotify']
            })
    
    all_data.append(sport_data)

# Save JSON
with open("spotify_songs.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

# Save CSV
with open("spotify_songs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Sport", "Song", "Artist", "Album", "Spotify URL", "Scraped At"])
    for entry in all_data:
        for song in entry["songs"]:
            writer.writerow([
                entry["sport"], 
                song["song"], 
                song["artist"], 
                song["album"], 
                song["url"], 
                entry["scraped_at"]
            ])

print("✅ Done! Data saved to spotify_songs.json and spotify_songs.csv")
