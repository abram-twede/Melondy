import os

import openai
from flask import Flask, redirect, render_template, request, url_for

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    return render_template("index.html", result=result)


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
