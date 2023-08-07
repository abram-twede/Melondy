![Words](https://github.com/ajtwede/Melondy/assets/69599409/6095598d-10a2-4b82-9c7c-f15ec7b5d0a1)


##MELONDY
This is a python app that uses open ai api and spotify api. It also uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework. Follow the instructions below to get set up.

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   $ cd - Melondy
   ```

4. Create a new virtual environment:

   ```bash
   $ python3 -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://platform.openai.com/account/api-keys) to the newly created `.env` file.

8. Go to developer.spotify.com and add your API keys to the .env file

9. Run the app:

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)! 
