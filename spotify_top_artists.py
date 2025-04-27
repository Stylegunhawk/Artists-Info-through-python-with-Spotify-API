import requests
import base64
import json
import webbrowser
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# Define the scope of permissions we need
SCOPE = 'user-read-private user-read-email playlist-read-private playlist-read-collaborative'

# File to save the access token
TOKEN_FILE = 'access_token.json'

def get_auth_url():
    """Generate the authorization URL for Spotify login"""
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'show_dialog': True
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    return auth_url

def get_token(auth_code):
    """Exchange the authorization code for an access token"""
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    return response.json()

def get_popular_artists(token, limit=10):
    """Get globally popular artists from new releases on Spotify"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Get new album releases
    print(f"\nRequesting new releases with token: {token[:10]}...")
    response = requests.get(f"{API_BASE_URL}browse/new-releases?limit=20&country=US", headers=headers)
    print(f"New releases response status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error getting new releases: {response.json()}")
        return {"items": []}
    
    albums = response.json().get('albums', {}).get('items', [])
    if not albums:
        print("No new releases found")
        return {"items": []}
    
    print(f"Found {len(albums)} new release albums")
    
    # Extract unique artists from the albums
    artists = {}
    for album in albums:
        if 'artists' in album:
            for artist in album['artists']:
                if artist['id'] not in artists and len(artists) < limit:
                    try:
                        # Get full artist details
                        artist_response = requests.get(f"{API_BASE_URL}artists/{artist['id']}", headers=headers)
                        if artist_response.status_code == 200:
                            artists[artist['id']] = artist_response.json()
                            # Use ASCII-only representation for console output
                            artist_name = artist['name'].encode('ascii', 'replace').decode('ascii')
                            print(f"Got details for artist: {artist_name}")
                    except Exception as e:
                        print(f"Error getting details for an artist: {str(e)}")
    
    # Format the response similar to the top artists endpoint
    result = {"items": list(artists.values())}
    print(f"Found {len(result['items'])} unique artists")
    return result

def display_artists(artists_data):
    """Display the artists information"""
    if 'items' not in artists_data:
        print("Error retrieving artists:", artists_data)
        return
    
    if len(artists_data['items']) == 0:
        print("\nNo artists found. This could be because:")
        print("1. There might be an issue with the API request")
        print("2. The new releases might not have enough unique artists")
        return
    
    print("\n===== POPULAR SPOTIFY ARTISTS =====\n")
    for i, artist in enumerate(artists_data['items'], 1):
        try:
            # Use ASCII-only representation for console output
            artist_name = artist['name'].encode('ascii', 'replace').decode('ascii')
            print(f"{i}. {artist_name}")
            print(f"   Popularity: {artist['popularity']}/100")
            print(f"   Followers: {artist['followers']['total']:,}")
            
            # Handle genres safely
            genres = []
            for genre in artist['genres']:
                try:
                    genres.append(genre.encode('ascii', 'replace').decode('ascii'))
                except:
                    genres.append('[non-ascii-genre]')
            
            print(f"   Genres: {', '.join(genres)}")
            
            if artist['images']:
                print(f"   Image: {artist['images'][0]['url']}")
            print()
        except Exception as e:
            print(f"Error displaying artist {i}: {str(e)}")
            print()

def show_auth_url():
    """Step 1: Get and display authorization URL for the user to visit"""
    auth_url = get_auth_url()
    print("\nPlease visit this URL to authorize the application:")
    print(auth_url)
    webbrowser.open(auth_url)
    print("\nAfter authorizing, you will be redirected to a URL like:")
    print(f"{REDIRECT_URI}?code=AQD...long-code-here...")
    print("\nCopy the entire code parameter value (everything after 'code=') and run:")
    print("python spotify_top_artists.py --code YOUR_AUTHORIZATION_CODE")
    return True

def process_auth_code(auth_code):
    """Process the authorization code provided as a command-line argument"""
    # Exchange the authorization code for an access token
    token_data = get_token(auth_code)
    if 'access_token' not in token_data:
        print("Error getting access token:", token_data)
        return False
    
    # Save the token data to a file
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)
    
    print("\nAuthorization successful! Token saved to", TOKEN_FILE)
    return True

def refresh_token(refresh_token_str):
    """Refresh the access token using the refresh token"""
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token_str
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    return response.json()

def get_valid_token():
    """Get a valid access token, refreshing if necessary"""
    if not os.path.exists(TOKEN_FILE):
        print("No saved token found. Please run the authorization step first.")
        return None
    
    # Load the token data from the file
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)
    
    if 'access_token' not in token_data:
        print("Invalid token data. Please run the authorization step again.")
        return None
    
    # Check if we have a refresh token
    if 'refresh_token' in token_data:
        # Try to use the access token
        access_token = token_data['access_token']
        
        # Make a simple API call to check if the token is still valid
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(f"{API_BASE_URL}me", headers=headers)
        
        # If the token is expired, refresh it
        if response.status_code == 401:
            print("Access token expired. Refreshing...")
            new_token_data = refresh_token(token_data['refresh_token'])
            
            if 'access_token' in new_token_data:
                # Update the access token
                token_data['access_token'] = new_token_data['access_token']
                
                # Update the refresh token if a new one was provided
                if 'refresh_token' in new_token_data:
                    token_data['refresh_token'] = new_token_data['refresh_token']
                
                # Save the updated token data
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(token_data, f)
                
                print("Token refreshed successfully!")
                return token_data['access_token']
            else:
                print("Error refreshing token:", new_token_data)
                return None
        
        return access_token
    else:
        print("No refresh token found. Please run the authorization step again.")
        return None

def get_popular_artists_with_saved_token():
    """Use the saved token to get and display popular artists"""
    access_token = get_valid_token()
    if not access_token:
        return False
    
    # Get popular artists
    artists_data = get_popular_artists(access_token)
    
    # Display the artists
    display_artists(artists_data)
    return True

def search_artist(token, query):
    """Search for an artist by name and allow user to pick the correct one"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Search for the artist
    print(f"\nSearching for artist: {query}...")
    params = {
        'q': query,
        'type': 'artist',
        'limit': 5  # Get the top 5 matches
    }
    response = requests.get(f"{API_BASE_URL}search", headers=headers, params=params)
    print(f"Search response status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error searching for artist: {response.json()}")
        return None
    
    # Check if we found any artists
    artists = response.json().get('artists', {}).get('items', [])
    if not artists:
        print(f"No artists found matching '{query}'")
        return None
    
    # Show top 5 matches and let user pick
    print("\nTop 5 artist matches:")
    for idx, artist in enumerate(artists, 1):
        name = artist['name']
        url = artist['external_urls']['spotify']
        genres = ', '.join(artist['genres']) if artist['genres'] else 'N/A'
        print(f"{idx}. {name} | Genres: {genres} | Popularity: {artist['popularity']} | Spotify: {url}")
    
    # Get user choice
    while True:
        try:
            selection = int(input(f"\nSelect the correct artist (1-{len(artists)}): "))
            if 1 <= selection <= len(artists):
                break
            else:
                print("Invalid selection. Try again.")
        except Exception:
            print("Please enter a valid number.")
    
    artist = artists[selection-1]
    artist_id = artist['id']
    print(f"You selected: {artist['name']} (ID: {artist_id})")
    
    # Get the artist's top tracks (limited to 5)
    print(f"Getting top tracks for {artist['name']}...")
    response = requests.get(f"{API_BASE_URL}artists/{artist_id}/top-tracks?country=US", headers=headers)
    
    if response.status_code != 200:
        print(f"Error getting top tracks: {response.json()}")
        top_tracks = []
    else:
        # Limit to top 5 tracks
        top_tracks = response.json().get('tracks', [])[:5]
    
    # Add top tracks to the artist object
    artist['top_tracks'] = top_tracks
    
    # Get related artists (robust)
    print(f"Getting related artists for {artist['name']}...")
    related_url = f"{API_BASE_URL}artists/{artist_id}/related-artists"
    try:
        related_resp = requests.get(related_url, headers=headers)
        if related_resp.status_code == 200:
            related_artists = related_resp.json().get('artists', [])
        elif related_resp.status_code == 404:
            print("Related artists are not available for this artist due to Spotify API limitations.")
            related_artists = None  # Use None to distinguish this case
        else:
            print(f"Error getting related artists: {related_resp.json()}")
            related_artists = []
    except Exception as e:
        print(f"Exception getting related artists: {e}")
        related_artists = []
    artist['related_artists'] = related_artists
    
    # Get artist's albums (limited to 2)
    print(f"Getting albums for {artist['name']}...")
    albums_url = f"{API_BASE_URL}artists/{artist_id}/albums"
    albums_params = {'limit': 10, 'include_groups': 'album'}
    albums_resp = requests.get(albums_url, headers=headers, params=albums_params)
    albums = []
    if albums_resp.status_code == 200:
        seen = set()
        for album in albums_resp.json().get('items', []):
            if album['name'] not in seen:
                albums.append(album)
                seen.add(album['name'])
            if len(albums) == 2:
                break
    else:
        print(f"Error getting albums: {albums_resp.json()}")
    artist['albums'] = albums
    
    # Try to get concert information (this is a simulation as Spotify API doesn't provide this)
    artist['concerts'] = []
    # Just print a message about this limitation in the display function instead
    
    return artist

def display_artist_details(artist, token):
    """Display detailed information about an artist"""
    if not artist:
        return
    
    try:
        print(f"\n===== ARTIST DETAILS: {artist['name']} =====\n")
        print(f"Popularity: {artist['popularity']}/100")
        print(f"Followers: {artist['followers']['total']:,}")
        
        # Display genres
        genres = ', '.join(artist['genres']) if artist['genres'] else 'N/A'
        print(f"Genres: {genres}")
        print(f"Spotify URL: {artist['external_urls']['spotify']}")
        
        # Display artist image
        if artist.get('images') and len(artist['images']) > 0:
            print(f"Image: {artist['images'][0]['url']}")
        else:
            print("No artist image available.")
            
        # Display top tracks with audio features
        if artist['top_tracks']:
            print("\n===== TOP SONGS =====")
            for idx, track in enumerate(artist['top_tracks'][:5], 1):
                print(f"{idx}. {track['name']}")
                print(f"   Spotify URL: {track['external_urls']['spotify']}")
                if track['album']['images']:
                    print(f"   Image: {track['album']['images'][0]['url']}")
                print(f"   Popularity: {track['popularity']}")
                print(f"   Album: {track['album']['name']}")

                if track['album']['images']:
                    print(f"   Image: {track['album']['images'][0]['url']}")
                print(f"   Preview: {track['preview_url'] if track['preview_url'] else 'Not available'}")

            
            # Display albums (top 2)
        if artist['albums']:
            print("\n===== TOP ALBUMS =====")
            for idx, album in enumerate(artist['albums'][:2], 1):
                print(f"{idx}. {album['name']}")
                print(f"   Release date: {album['release_date']}")
                if album['images']:
                    print(f"   Image: {album['images'][0]['url']}")
                print(f"   Spotify URL: {album['external_urls']['spotify']}")
        else:
            print("\nNo albums available")
        
        # Display related artists

        if artist.get('related_artists') is None:
            print("\nSpotify does not provide similar artists for this artist (API limitation).")
        elif artist.get('related_artists'):
            print("\n===== SIMILAR ARTISTS =====")
            for idx, rel in enumerate(artist['related_artists'][:5], 1):
                rel_name = rel.get('name', 'N/A')
                rel_pop = rel.get('popularity', 'N/A')
                rel_url = rel.get('external_urls', {}).get('spotify', 'N/A')
                print(f"{idx}. {rel_name} (Popularity: {rel_pop}) - {rel_url}")
        else:
            print("\nNo related artists available")
            
        # Display artist image, concert and about info via Spotify
        print("\n===== ARTIST ON TOUR & ABOUT INFO =====")
        if artist.get('images') and len(artist['images']) > 0:
            print(f"Artist Image: {artist['images'][0]['url']}")
        else:
            print("No artist image available.")
        print(f"Visit the artist's official Spotify page for tour dates and biography:")
        print(f"{artist['external_urls']['spotify']}")
        print("Look for the 'On Tour' and 'About' sections on the Spotify page.")
    except Exception as e:
        print(f"Error displaying artist details: {str(e)}")

def get_user_playlists(token, limit=50):
    """Get the user's playlists"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print(f"\nGetting your playlists...")
    response = requests.get(f"{API_BASE_URL}me/playlists?limit={limit}", headers=headers)
    print(f"Playlists response status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error getting playlists: {response.json()}")
        return []
    
    playlists = response.json().get('items', [])
    print(f"Found {len(playlists)} playlists")
    return playlists

def display_playlists(playlists):
    """Display a list of playlists"""
    if not playlists:
        print("No playlists found")
        return
    
    print("\n===== YOUR PLAYLISTS =====\n")
    for i, playlist in enumerate(playlists, 1):
        try:
            name = playlist['name'].encode('ascii', 'replace').decode('ascii')
            print(f"{i}. {name}")
            print(f"   Tracks: {playlist['tracks']['total']}")
            print(f"   Public: {playlist['public']}")
            print(f"   Collaborative: {playlist['collaborative']}")
            if playlist['images']:
                print(f"   Image: {playlist['images'][0]['url'] if playlist['images'] else 'No image'}")
            print()
        except Exception as e:
            print(f"Error displaying playlist {i}: {str(e)}")

def search_artist_with_saved_token():
    """Use the saved token to search for an artist"""
    access_token = get_valid_token()
    if not access_token:
        return False
    
    # Get the search query from the user
    query = input("Enter an artist name or song title to search: ")
    if not query:
        print("No search query provided")
        return False
    
    # Search for the artist
    artist = search_artist(access_token, query)
    
    # Display the artist details
    display_artist_details(artist, access_token)

    # Save only displayed artist info in saved_artists.json, with artist name as top-level key
    import os, json
    json_file = "saved_artists.json"
    # Load existing data if present
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            all_artists = json.load(f)
    else:
        all_artists = {}

    # Build the minimal info dict for this artist
    artist_name = artist.get('name', 'Unknown Artist')
    minimal_artist = {
        "id": artist.get('id'),
        "name": artist_name,
        "spotify_url": artist.get('external_urls', {}).get('spotify'),
        "popularity": artist.get('popularity'),
        "followers": artist.get('followers', {}).get('total'),
        "genres": artist.get('genres'),
        "image_url": artist.get('images', [{}])[0].get('url') if artist.get('images') else None,
        "top_tracks": [],
        "albums": [],
        "related_artists": [ra.get('name') for ra in (artist.get('related_artists') or [])],
        "concerts": artist.get('concerts', [])
    }
    for track in artist.get('top_tracks', []):
        minimal_artist['top_tracks'].append({
            "name": track.get('name'),
            "album": track.get('album', {}).get('name'),
            "popularity": track.get('popularity'),
            "spotify_url": track.get('external_urls', {}).get('spotify'),
            "preview_url": track.get('preview_url'),
            "album_image_url": track.get('album', {}).get('images', [{}])[0].get('url') if track.get('album', {}).get('images') else None
        })
    for album in artist.get('albums', []):
        minimal_artist['albums'].append({
            "name": album.get('name'),
            "release_date": album.get('release_date'),
            "image_url": album.get('images', [{}])[0].get('url') if album.get('images') else None,
            "spotify_url": album.get('external_urls', {}).get('spotify')
        })
    # Save using artist name as key
    if artist_name not in all_artists:
        all_artists[artist_name] = minimal_artist
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_artists, f, indent=2, ensure_ascii=False)
        print(f"\nSaved artist '{artist_name}' to {json_file} (minimal info only).")
    else:
        print(f"\nArtist '{artist_name}' already exists in {json_file}, not saving duplicate.")

    # Print summary of all saved artists
    print("\nArtists currently saved:")
    for aname in all_artists:
        print(f"- {aname}")
    return True

def get_playlists_with_saved_token():
    """Use the saved token to get and display user playlists"""
    access_token = get_valid_token()
    if not access_token:
        return False
    
    # Get the user's playlists
    playlists = get_user_playlists(access_token)
    
    # Display the playlists
    display_playlists(playlists)
    return True

def show_menu():
    """Show an interactive menu for the user"""
    while True:
        print("\n===== SPOTIFY API EXPLORER =====")
        print("1. Get popular artists")
        print("2. View your playlists")
        print("3. Search for an artist (detailed info)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            get_popular_artists_with_saved_token()
        elif choice == '2':
            get_playlists_with_saved_token()
        elif choice == '3':
            search_artist_with_saved_token()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    # Check if we have command line arguments
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auth":
        # Just show the authorization URL
        show_auth_url()
    elif len(sys.argv) > 1 and sys.argv[1] == "--code" and len(sys.argv) > 2:
        # Process the authorization code
        auth_code = sys.argv[2]
        if process_auth_code(auth_code):
            # If authorization was successful, show the menu
            show_menu()
    elif len(sys.argv) > 1 and sys.argv[1] == "--artists":
        # Run the get popular artists step
        get_popular_artists_with_saved_token()
    elif len(sys.argv) > 1 and sys.argv[1] == "--playlists":
        # Run the get playlists step
        get_playlists_with_saved_token()
    elif len(sys.argv) > 1 and sys.argv[1] == "--search":
        # Run the search artist step
        search_artist_with_saved_token()
    elif len(sys.argv) > 1 and sys.argv[1] == "--menu":
        # Show the interactive menu
        show_menu()
    else:
        # No arguments, show usage
        print("Usage:")
        print("  python spotify_top_artists.py --auth             # Get authorization URL")
        print("  python spotify_top_artists.py --code AUTH_CODE  # Process authorization code")
        print("  python spotify_top_artists.py --artists         # Get and display popular artists")
        print("  python spotify_top_artists.py --playlists       # Get and display your playlists")
        print("  python spotify_top_artists.py --search          # Search for an artist")
        print("  python spotify_top_artists.py --menu            # Show interactive menu")

if __name__ == "__main__":
    main()
