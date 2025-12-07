import os
import streamlit as st
from backend.database import get_database
from backend.crud import AuthService
from backend.auth_utils import hash_password, verify_password

def render_login():
    """Render the login page."""
    # Add custom CSS for better styling
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem 0;
        }
        .auth-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .auth-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1.5rem 0;
        }
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ddd;
        }
        .divider span {
            padding: 0 1rem;
            color: #666;
            font-size: 0.875rem;
        }
        .google-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 12px 24px;
            background: white;
            border: 1px solid #dadce0;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #3c4043;
            text-decoration: none;
            transition: all 0.15s ease;
        }
        .google-btn:hover {
            background: #f8f9fa;
            border-color: #d2d3d4;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
        }
        .google-btn img {
            width: 18px;
            height: 18px;
            margin-right: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-title">🤖 Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Sign in to continue to TaskAssignAI</p>', unsafe_allow_html=True)
        
        # Google Sign-in Button
        oauth_url = os.getenv('OAUTH_SERVER_URL', 'http://localhost:8502')
        st.markdown(f"""
        <a href="{oauth_url}/auth/google/login" class="google-btn" target="_self">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google"/>
            <span>Continue with Google</span>
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"><span>OR</span></div>', unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    db = get_database()
                    session = db.get_session()
                    auth_service = AuthService(session)
                    user = auth_service.get_user_by_username(username)
                    
                    if user and verify_password(password, user.password_hash):
                        st.session_state.user_id = user.id
                        st.session_state.username = user.username
                        st.session_state.logged_in = True
                        session.close()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        session.close()
                        st.error("Invalid username or password.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Sign up link
        st.markdown("<br>", unsafe_allow_html=True)
        col_x, col_y, col_z = st.columns([1, 2, 1])
        with col_y:
            if st.button("Don't have an account? Sign Up", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()


def render_signup():
    """Render the signup page."""
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-title">📝 Create Account</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Join TaskAssignAI today</p>', unsafe_allow_html=True)
        
        # Signup Form
        with st.form("signup_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    db = get_database()
                    session = db.get_session()
                    auth_service = AuthService(session)
                    
                    if auth_service.get_user_by_username(username):
                        session.close()
                        st.error("Username already exists.")
                    else:
                        hashed = hash_password(password)
                        user = auth_service.create_user(username, hashed)
                        session.close()
                        
                        st.success("Account created! Redirecting to login...")
                        st.session_state.auth_mode = "login"
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Login link
        st.markdown("<br>", unsafe_allow_html=True)
        col_x, col_y, col_z = st.columns([1, 2, 1])
        with col_y:
            if st.button("Already have an account? Sign In", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

