import google.oauth2.credentials
import google_auth_oauthlib.flow
import environment as env
import logging



SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.appdata'] 


def get_authorization_url():
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        env.oauth_client_secret_file,
        scopes=SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = env.callback_URI

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return authorization_url, state


def get_credentials(request_url, state):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        env.oauth_client_secret_file,
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = env.callback_URI

    authorization_response = request_url
    try:
        flow.fetch_token(authorization_response=authorization_response) 
        credentials = flow.credentials
        credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': str(credentials.expiry)}
        return credentials
    except Exception as e:
        logging.error("Error while exchanging the authorization code " + str(e))
        return None


    