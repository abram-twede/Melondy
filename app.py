from flask import Flask, request, redirect, session, render_template, url_for
import spotipy
import openai
import os
from spotipy.oauth2 import SpotifyOAuth
import json


app = Flask(__name__)
app.secret_key = os.getenv('APP_CLIENT_SECRET')
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_spotify_oauth():
    return SpotifyOAuth(
        scope='playlist-modify-public user-read-email user-read-playback-state user-modify-playback-state'
    )

@app.route('/login')
def login():
    if 'token_info' in session:
        print("one:",token_info)
        return redirect(url_for('home')) 
        
    else:
        sp_oauth = create_spotify_oauth()
        code = request.args.get('code')
        if code:
            token_info = sp_oauth.get_access_token(code=code)
            session["token_info"] = token_info
            print("two:",token_info)
            return redirect(url_for('home'))
        else:
            auth_url = sp_oauth.get_authorize_url()
            print("three:",auth_url)
            return redirect(auth_url, code=302)

@app.route('/', methods=['GET', 'POST'])
def home():
    # spotify = get_spotify()
    # currentuser = spotify.current_user()
    suggestions = []

    if request.method == 'POST':
        song = request.form.get('song')
        suggestions = generate_suggestions(song)

    return render_template('index.html', suggestions=suggestions)  

def generate_prompt(song):
    return "Suggest 5 songs that are similar to {}. and add a newline after each item".format(song.capitalize())

@app.route('/about')
def about():
    return render_template('about.html')

def get_spotify():
    sp_oauth = create_spotify_oauth()
    token_info = session.get('token_info', None)

    if not token_info:
        print("No token_info in session.")
        return None

    if sp_oauth.is_token_expired(token_info):
        print("Token expired.")
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session["token_info"] = token_info  # Save the new token info in session

    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/playlists')
def playlists():
    spotify = get_spotify()
    return render_template('playlists.html', playlists=spotify.current_user_playlists())

@app.route('/suggestions',methods=['GET', 'POST'])
def suggestions():
    spotify = get_spotify()
    if spotify is None: 
        return redirect(url_for('login'))
    
    
    playlist_uri = request.args.get('playlist_uri')
    
    playlist = request.args.get('playlist')
    if request.method == 'POST':
        
        # Collect the selected songs
        selected_uris = request.form.getlist('selection')
        playlist_uri = request.form.get('playlist_uri')
        playlist = request.form.get('playlist')
        print("playlist_uri:",playlist_uri)
        # Convert song names to URIs
        # song_uris = []
        # for song in selected_uris:
        #     result = spotify.search(q='track:' + song, type='track')
        #     if result['tracks']['items']:
        #         song_uris.append(result['tracks']['items'][0]['uri'])
        
        # Add songs to playlist
        if selected_uris:
            current_user = spotify.current_user()
            spotify.user_playlist_add_tracks(current_user['id'], playlist_uri.split(':')[2], selected_uris)
        else:
            print("No songs selected")

        
    SpotifyResults = spotify.playlist_items(playlist_uri)
    songs = ""
    for item in SpotifyResults['items']:
        track = item['track']['name']
        songs += track + "\n"
    GPTresults = generate_suggestions(songs)

    suggestions = []

    for GPTresult in GPTresults:
        suggestion = {}

        data = GPTresult.split(' - ')

        track = data[0]
        suggestion['track'] = track
        query = "track:" + track 
        if len(data) > 1:
            artist = data[1]
            suggestion['artist'] = artist
            query += " artist:" + artist
            
       
        SpotifyResults = spotify.search(q=query,limit=1, type='track', market='US')
        
        if SpotifyResults['tracks']['items']:
                song_uri = (SpotifyResults['tracks']['items'][0]['uri'])
                print("song_uri:",song_uri)
                suggestion['uri'] = song_uri
                song_url= (SpotifyResults['tracks']['items'][0]['external_urls']['spotify'])
                print("song_url:",song_url)
                suggestion['url'] = song_url

        suggestions.append(suggestion)
        


    return render_template('suggestions.html', suggestions=suggestions, playlist_uri=playlist_uri, playlist = playlist)


def generate_suggestions(songs):
    prompt = "Respond with song and artist (for example: 'Radioactive - Imagine Dragons') - based on the songs given provide a list of 5 new songs with artists that fit the same style and genre do not repeat songs that are given and add a newline after each item: {} . only respond with the songs".format(songs)
    response = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=256
    )
    suggestions = response['choices'][0]['message']['content'].split('\n')[:5]

    

        

    return suggestions

if __name__ == "__main__":
    with app.app_context():  # Creating application context
        app.run(debug=True)

