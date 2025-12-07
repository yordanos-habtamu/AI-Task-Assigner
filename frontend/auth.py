import streamlit as st
from backend.database import get_database
from backend.crud import AuthService
from backend.auth_utils import hash_password, verify_password

def render_login():
    """Render the login page."""
    st.markdown("## 🔐 Login to TaskAssignAI")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
                return
            
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
    
    st.markdown("---")
    st.markdown("### Social Login (Demo)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign in with GitHub", use_container_width=True):
            st.info("GitHub OAuth would redirect here. (Placeholder)")
    with col2:
        if st.button("Sign in with Google", use_container_width=True):
            st.info("Google OAuth would redirect here. (Placeholder)")
            
    st.markdown("---")
    if st.button("Don't have an account? Sign Up"):
        st.session_state.auth_mode = "signup"
        st.rerun()

def render_signup():
    """Render the signup page."""
    st.markdown("## 📝 Create Account")
    
    with st.form("signup_form"):
        username = st.text_input("Choose Username")
        password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please fill in all fields.")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
                
            db = get_database()
            session = db.get_session()
            auth_service = AuthService(session)
            
            if auth_service.get_user_by_username(username):
                session.close()
                st.error("Username already exists.")
                return
            
            hashed = hash_password(password)
            user = auth_service.create_user(username, hashed)
            session.close()
            
            st.success("Account created! Please login.")
            st.session_state.auth_mode = "login"
            st.rerun()
            
    if st.button("Already have an account? Login"):
        st.session_state.auth_mode = "login"
        st.rerun()
