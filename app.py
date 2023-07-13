from flask import Flask, request, redirect, session, render_template, url_for
import spotipy
import openai
import os
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = os.getenv('APP_CLIENT_SECRET')
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_spotify_oauth():
    return SpotifyOAuth(
        scope='playlist-modify-public user-read-email'
    )

@app.route('/')
def login():
    if 'token_info' in session:
        return redirect(url_for('create_playlist')) 
    else:
        sp_oauth = create_spotify_oauth()
        code = request.args.get('code')
        if code:
            token_info = sp_oauth.get_access_token(code=code)
            session["token_info"] = token_info
            return redirect(url_for('create_playlist'))
        else:
            auth_url = sp_oauth.get_authorize_url()
            return render_template('login.html', auth_url=auth_url)  

# @app.route('/callback')
# def callback():
#     sp_oauth = create_spotify_oauth()
#     session.clear()
#     code = request.args.get('code')
#     token_info = sp_oauth.get_access_token(code=code)
#     session["token_info"] = token_info
#     return redirect(url_for('create_playlist'))

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    spotify = get_spotify()
    currentuser = spotify.current_user()
    print( "user " + str(currentuser))
    if request.method == 'POST':
        song = request.form.get('song')
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(song),
            temperature=0.6,
            max_tokens=256
        )
        result = response.choices[0].text
        print(result)
        return redirect(url_for("create_playlist", result=result))
    result = request.args.get("result")
    return render_template('index.html', result=result)  

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

def generate_prompt(song):
    return "Suggest 5 songs that are similar to {}. and add a newline after each item".format(song.capitalize())

if __name__ == "__main__":
    with app.app_context():  # Creating application context
        app.run(debug=True)

@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/playlists')
# def playlists():
##     cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
#     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
#     if not auth_manager.validate_token(cache_handler.get_cached_token()):
#         return redirect('/')

#     spotify = spotipy.Spotify(auth_manager=auth_manager)
#     return spotify.current_user_playlists()

# @app.route('/current_user')
# def current_user():
#     cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
#     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
#     if not auth_manager.validate_token(cache_handler.get_cached_token()):
#         return redirect('/')
#     spotify = spotipy.Spotify(auth_manager=auth_manager)
#     return spotify.current_user()

def get_spotify():
    sp_oauth = create_spotify_oauth()
    
    if not sp_oauth.validate_token(session.get('token_info')):
        print("token.valid is false")
        logout()
    else:
        return spotipy.Spotify(auth_manager=sp_oauth)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# get  user playlists
@app.route('/playlists')
def playlists():
    spotify = get_spotify()
    return render_template('playlists.html', playlists=spotify.current_user_playlists())

@app.route('/suggestions')
def suggestions():
    spotify = get_spotify()
    playlist_uri = request.args.get('playlist_uri')
    results = spotify.playlist_items(playlist_uri)
    songs = ""
    for item in results['items']:
        track = item['track']['name']
        songs += track + "\n"

    prompt = generate_suggestions(songs)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": generate_suggestions(songs)}
        ],
        temperature=1,
        max_tokens=256
    )
    #parse response to get 5 songs
    suggestions = response['choices'][0]['message']['content'].split('\n')[:5]
    print(suggestions)
    return render_template('suggestions.html', suggestions=suggestions)

def generate_suggestions(songs):
    prompt = "based on the songs given provide a list of 5 new songs with artists that fit the same style and genre and add a newline after each item: {} . only respond with the songs".format(songs)
    return prompt