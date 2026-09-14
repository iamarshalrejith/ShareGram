import os
import streamlit as st
import requests

try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Media Feed", page_icon="📸", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login(email: str, password: str):
    resp = requests.post(
        f"{API_URL}/auth/jwt/login",
        data={"username": email, "password": password},
    )
    if resp.status_code == 200:
        st.session_state.token = resp.json()["access_token"]
        st.session_state.email = email
        return True, "Logged in."
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    return False, f"Login failed: {detail}"


def register(email: str, password: str):
    resp = requests.post(
        f"{API_URL}/auth/register",
        json={"email": email, "password": password},
    )
    if resp.status_code == 201:
        return True, "Account created. You can now log in."
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    return False, f"Registration failed: {detail}"


def logout():
    st.session_state.token = None
    st.session_state.email = None


def get_feed():
    resp = requests.get(f"{API_URL}/feed", headers=auth_headers())
    if resp.status_code == 401:
        logout()
        st.warning("Session expired. Please log in again.")
        st.rerun()
    resp.raise_for_status()
    return resp.json()["posts"]


def upload_post(file, caption):
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"caption": caption}
    resp = requests.post(f"{API_URL}/upload", files=files, data=data, headers=auth_headers())
    return resp


def delete_post(post_id):
    resp = requests.delete(f"{API_URL}/posts/{post_id}", headers=auth_headers())
    return resp


def auth_screen():
    st.title("📸 Media Feed")
    tab_login, tab_register = st.tabs(["Log in", "Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in")
            if submitted:
                ok, msg = login(email, password)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            password2 = st.text_input("Confirm password", type="password", key="reg_password2")
            submitted = st.form_submit_button("Create account")
            if submitted:
                if password != password2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register(email, password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def feed_screen():
    st.sidebar.write(f"Logged in as **{st.session_state.email}**")
    if st.sidebar.button("Log out"):
        logout()
        st.rerun()

    st.title("📸 Media Feed")

    with st.expander("Upload a new post", expanded=False):
        with st.form("upload_form", clear_on_submit=True):
            file = st.file_uploader("Choose an image or video", type=["png", "jpg", "jpeg", "gif", "mp4", "mov"])
            caption = st.text_input("Caption")
            submitted = st.form_submit_button("Upload")
            if submitted:
                if not file:
                    st.error("Please choose a file first.")
                else:
                    with st.spinner("Uploading..."):
                        resp = upload_post(file, caption)
                    if resp.status_code == 200:
                        st.success("Uploaded!")
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        st.error(f"Upload failed: {detail}")

    st.divider()

    try:
        posts = get_feed()
    except requests.RequestException as e:
        st.error(f"Could not reach the API: {e}")
        return

    if not posts:
        st.info("No posts yet. Be the first to upload something!")
        return

    for post in posts:
        with st.container(border=True):
            if post["file_type"] == "video":
                st.video(post["url"])
            else:
                st.image(post["url"])

            if post.get("caption"):
                st.write(post["caption"])
            st.caption(post["created_at"])

            if post.get("is_owner"):
                if st.button("Delete", key=f"delete_{post['id']}"):
                    resp = delete_post(post["id"])
                    if resp.status_code == 200:
                        st.success("Deleted.")
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        st.error(f"Delete failed: {detail}")


if st.session_state.token:
    feed_screen()
else:
    auth_screen()