import flask
from os import getcwd, path, environ
from google_auth_oauthlib.flow import Flow
from app.lib.config import read_from_env
from app.lib.calendar import SCOPES
import webbrowser
from sys import exit

config = read_from_env()

oauth_secrets = path.join(getcwd(), config.google.oauth_secrets)
tokens = path.join(getcwd(), config.google.tokens)

app = flask.Flask(__name__)
app.secret_key = config.google.oauth_flask_secret_key


@app.route("/oauth_callback")
def oauth_callback():
    print("oauth_callback request")
    state = flask.session["state"]
    flow = Flow.from_client_secrets_file(oauth_secrets, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for("oauth_callback", _external=True)
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials_json = flow.credentials.to_json()
    print("writing tokens")
    with open(tokens, "w+") as f:
        f.write(credentials_json)
    print("tokens written")
    exit()


@app.route("/authorize")
def authorize():
    print("authorize request")
    flow = Flow.from_client_secrets_file(oauth_secrets, scopes=SCOPES)
    flow.redirect_uri = flask.url_for("oauth_callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    flask.session["state"] = state
    print(f"redirecting to {authorization_url}")
    return flask.redirect(authorization_url)


if __name__ == "__main__":
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    webbrowser.open("http://localhost:6080/authorize")
    app.run("localhost", 6080, debug=True)
