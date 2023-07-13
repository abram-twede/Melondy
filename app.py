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
        return redirect(url_for('login'))  

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