"""
OAuth Server for Google SSO
Runs alongside Streamlit to handle OAuth callbacks.
"""

import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, redirect, request, url_for, session
from authlib.integrations.flask_client import OAuth
from backend.database import get_database
from backend.crud import AuthService

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Session tokens (in-memory for simplicity, use Redis in production)
auth_tokens = {}


@app.route('/auth/google/login')
def google_login():
    """Initiate Google OAuth flow."""
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return "Authentication failed: No user info received", 400
        
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Store or retrieve user in database
        db = get_database()
        db_session = db.get_session()
        auth_service = AuthService(db_session)
        
        # Check if user exists by email (stored as username for OAuth users)
        user = auth_service.get_user_by_username(email)
        
        if not user:
            # Create new user (no password needed for OAuth)
            user = auth_service.create_user(
                username=email,
                password_hash="OAUTH_USER"  # Placeholder for OAuth users
            )
        
        db_session.close()
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        auth_tokens[session_token] = {
            'user_id': user.id,
            'username': user.username,
            'expires_at': datetime.utcnow() + timedelta(hours=24)
        }
        
        # Redirect back to Streamlit with token
        streamlit_url = os.getenv('STREAMLIT_URL', 'http://localhost:8501')
        return redirect(f"{streamlit_url}?auth_token={session_token}")
        
    except Exception as e:
        return f"Authentication failed: {str(e)}", 400


@app.route('/auth/verify')
def verify_token():
    """Verify an auth token (called by Streamlit)."""
    token = request.args.get('token')
    
    if not token or token not in auth_tokens:
        return {'valid': False}, 401
    
    token_data = auth_tokens[token]
    
    # Check expiry
    if datetime.utcnow() > token_data['expires_at']:
        del auth_tokens[token]
        return {'valid': False}, 401
    
    # Clean up token after verification (single use)
    user_data = auth_tokens.pop(token)
    
    return {
        'valid': True,
        'user_id': user_data['user_id'],
        'username': user_data['username']
    }


@app.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'service': 'oauth-server'}


if __name__ == '__main__':
    port = int(os.getenv('OAUTH_PORT', 8502))
    app.run(host='0.0.0.0', port=port, debug=True)
