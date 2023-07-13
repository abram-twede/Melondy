import os
import openai
from flask import Flask,request, redirect, session, render_template, request, url_for

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
sp_oauth = SpotifyOAuth(
    client_id='your-spotify-client-id',
    client_secret='your-spotify-client-secret',
    redirect_uri=url_for('callback', _external=True),
    scope='playlist-modify-public user-read-email'
)


@app.route("/", methods=("GET", "POST"))
def index():
    sp_test()
    if request.method == "POST":
        song = request.form["animal"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(song),
            temperature=0.6,
            max_tokens=256

        )
        result = response.choices[0].text
        print(result)
        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template('index.html', result=result)


def generate_prompt(song):
    result = "Suggest 5 songs that are similar to {}. and add a newline after each item".format(song.capitalize())
    print(result)
    return result

def sp_test() :
    # auth_manager = SpotifyClientCredentials()
    # sp = spotipy.Spotify(auth_manager=auth_manager)

    # playlists = sp.user_playlists('spotify')

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlists = sp.user_playlists('spotify')
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    # urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
    # auth_manager = SpotifyClientCredentials()
    # sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # artist = sp.artist(urn)
    # print(artist)

    # user = sp.user('plamere')
    # print(user)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    # Render the login.html template with auth_url as a parameter
    return render_template('login.html', auth_url=auth_url)