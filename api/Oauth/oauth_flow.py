import google.oauth2.credentials
import google_auth_oauthlib.flow
from environment import conf
import logging
import datetime



SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.appdata'] 

class AuthorizationCodeExchangeError(Exception):
    """Raised when the authorization code exchange fails."""
    pass 

class NoRefreshTokenError(Exception):
    """Raised when the authorization code exchange does not return a refresh token."""
    pass


    



def get_authorization_url(): # pragma: no cover
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        conf.features.google_drive.client_secret_file_path,
        scopes=SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = conf.environment.callback_URI

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return authorization_url, state


def get_credentials(request_url, state): # pragma: no cover
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
         conf.features.google_drive.client_secret_file_path,
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = conf.environment.callback_URI

    if(conf.environment.type != "local"):
        # we force https in production
        authorization_response = request_url.replace('http://', 'https://')
    else:
        authorization_response = request_url
    try:
        flow.fetch_token(authorization_response=authorization_response) 
    except Exception as e:
        logging.error(f"Error exchanging authorization code: {e}")
        raise AuthorizationCodeExchangeError(f"Failed to exchange authorization code: {e}") from e
    credentials = flow.credentials
    if credentials is None:
        logging.warning("Getting credentials failed. No credentials received. The user will be asked to re-authorize the application.")
        raise AuthorizationCodeExchangeError("Failed to get credentials. Please re-authorize the application.")
    if credentials.token is None or credentials.expiry is None or credentials.client_id is None or credentials.client_secret is None or not credentials.scopes or len(credentials.scopes) == 0 or credentials.token_uri is None:
        logging.warning("Getting credentials failed. Missing token, expiry, client_id or client_secret or scopes or token_uri. The user will be asked to re-authorize the application.")
        raise AuthorizationCodeExchangeError("Failed to get valid credentials. Please re-authorize the application.")
    if credentials.refresh_token is None:
        logging.warning("Getting credentials failed. No refresh token received. The user will be asked to re-authorize the application.")
        raise NoRefreshTokenError()
    credentials = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': str(credentials.expiry)}
    return credentials
    


    