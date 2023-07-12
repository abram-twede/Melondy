
from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'CLIENT_SECRET'  

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='my-spotify-client-id',
        client_secret='my-spotify-client-secret',
        redirect_uri=url_for('callback', _external=True),
        scope='playlist-modify-public user-read-email'
    )

@app.route('/')
def index():
    if 'token_info' in session:
        return redirect(url_for('create_playlist'))  # If the user is already logged in, redirect to create_playlist page.
    else:
        sp_oauth = create_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return render_template('login.html', auth_url=auth_url)  # Render the login page with the Spotify login URL.

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code=code)
    session["token_info"] = token_info
    return redirect(url_for('create_playlist'))

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if 'token_info' not in session:
        return redirect(url_for('index'))  # If the user is not logged in, redirect to login page.

    if request.method == 'POST':
        song = request.form.get('song')
        # Here, you can add the logic for generating songs based on the input song.
        return render_template('index.html', result=song)  # Show the results on the same page.

    session["token_info"], authorized = get_token()
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    # Get user profile data
    user_profile = sp.current_user()
    user_id = user_profile['id']

    # Create a new playlist
    playlist = sp.user_playlist_create(user_id, "New Playlist")
    playlist_id = playlist['id']

    # TODO: Get track recommendations based on user profile and add them to the playlist
    # You'll need to implement your own logic here

    return render_template('index.html')  # Render the song input page.

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    sp_oauth = create_spotify_oauth()
    if token_info and not sp_oauth.is_token_expired(token_info):
        token_valid = True
    else:
        code = request.args.get('code')
        if code:
            token_info = sp_oauth.get_access_token(code=code)
            session["token_info"] = token_info
            token_valid = True

    return token_info, token_valid

if __name__ == "__main__":
    app.run(debug=True)
