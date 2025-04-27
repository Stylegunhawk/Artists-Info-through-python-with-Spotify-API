# Spotify Top Artists Explorer

A Python CLI tool that authenticates with your Spotify account, lets you search for artists, view their detailed info, and save only the essential artist data for future use. The tool manages access tokens securely, fetches top tracks, albums, and related artists, and deduplicates saved data by artist ID.

## Features
- **Artist Search:** Search for any artist by name or song title and view the top 5 matches.
- **Detailed Artist Info:** For a selected artist, display:
  - Popularity, followers, genres
  - Spotify profile link
  - Artist image
  - Top tracks (with album info, popularity, preview links)
  - Top albums (with release date, image, Spotify link)
  - Related artists (when available)
- **Save Artist Data:** Save artist information in a clean, deduplicated JSON file for future use. Only relevant fields are stored (no unnecessary data).
- **Error Handling:** Gracefully handles missing data, API limitations, and user input errors.

## Setup
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd spotify-final-try
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables:**
   - Create a `.env` file with your Spotify API credentials:
     ```env
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
     ```

## Usage
Run the CLI tool and follow the prompts:
```bash
python spotify_top_artists.py --search
```
- Use `--menu` for an interactive menu with multiple options.
- Saved artist data is written to `saved_artists.json` (deduplicated by artist ID).

## Example
```
Enter an artist name or song title to search: sia

Top 5 artist matches:
1. Sia | Genres: pop | Popularity: 86 | Spotify: https://open.spotify.com/artist/5WUlDfRSoLAfcVSX1WnrxN
...

===== ARTIST DETAILS: Sia =====
Popularity: 86/100
Followers: 29,763,921
Genres: pop
Spotify URL: https://open.spotify.com/artist/5WUlDfRSoLAfcVSX1WnrxN
...
```

## License
MIT
