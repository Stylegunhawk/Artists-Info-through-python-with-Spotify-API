<<<<<<< HEAD
# Spotify Top Artists Explorer

A Python CLI tool that authenticates with your Spotify account, lets you search for artists, view their detailed info, and save only the essential artist data for future use. The tool manages access tokens securely, fetches top tracks, albums, and related artists, and deduplicates saved data by artist ID.
=======
<<<<<<< HEAD
# Artists-Info-through-python-with-Spotify-API
=======
# Spotify Top Artists Explorer

A super easy Python command-line tool to search, view, and save detailed Spotify artist info. Authenticate once, and from then on, just run and explore!

---

## 🚀 Quick Start

1. **Clone this repo and enter the folder:**
   ```bash
   git clone https://github.com/Stylegunhawk/Artists-Info-through-python-with-Spotify-API.git
   cd Artists-Info-through-python-with-Spotify-API
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Spotify API credentials:**
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create an app and get your `Client ID`, `Client Secret`, and set the redirect URI to `http://localhost:8888/callback`.
   - Make a `.env` file in this folder:
     ```env
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
     ```

4. **First-time authentication:**
   ```bash
   python spotify_top_artists.py --auth
   # Follow the link, log in, copy the code from the URL
   python spotify_top_artists.py --code YOUR_AUTH_CODE
   ```
   After this, your tokens are saved securely. You only need to do this once!

5. **Explore artists, playlists, and more:**
   ```bash
   python spotify_top_artists.py --menu
   # Or search directly:
   python spotify_top_artists.py --search
   ```

---

## 🤖 How It Works
- After the first login, the script **automatically refreshes your token** when it expires. No need to log in again!
- All your artist info is saved and deduplicated by artist ID.
- You can:
  - Search for artists and view rich details
  - See your playlists
  - Discover popular artists

---
>>>>>>> legal-attribution

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
<<<<<<< HEAD
Run the CLI tool and follow the prompts:
```bash
python spotify_top_artists.py --search
```
- Use `--menu` for an interactive menu with multiple options.
- Saved artist data is written to `saved_artists.json` (deduplicated by artist ID).
=======

- **Interactive menu:**
  ```bash
  python spotify_top_artists.py --menu
  ```
- **Direct search for an artist:**
  ```bash
  python spotify_top_artists.py --search
  ```
- **Other options:**
  - `--artists` — Show popular artists
  - `--playlists` — Show your playlists

Saved artist data is written to `saved_artists.json` (deduplicated by artist ID).
>>>>>>> legal-attribution

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
=======
---

## 🛠 Troubleshooting
- **Token expired or invalid?** The script will refresh it automatically if you did the first login. If you ever get stuck, just repeat the authentication step.
- **.env not found?** Make sure you created it and filled in your Spotify credentials.- **Still stuck?** Open an issue or check your terminal for error messages.

## License
MIT

---

## Attribution & Legal

- This project uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api/). All artist and music data is provided by Spotify.
- This project is for personal and educational use only. Do **not** use it for commercial purposes without explicit permission from Spotify.
- Please review the [Spotify Developer Terms of Service](https://developer.spotify.com/terms/) if you plan to use this project in a public or commercial setting.
- Your authentication credentials and tokens are stored locally and never shared.
