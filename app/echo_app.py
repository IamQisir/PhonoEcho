import json
import streamlit as st
from time import sleep
import base64
from streamlit_extras.customize_running import center_running
from user import User

st.set_page_config(layout="wide", page_icon="logo/done_all.png")

# Function to load user_info from a JSON file
def load_user_info():
    """Load the user info."""
    try:
        with open("database/all_users/users_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to save user_info to a JSON file
def save_user_info(user_info):
    """Save the user info."""
    with open("database/all_users/users_info.json", "w") as f:
        json.dump(user_info, f, indent=4)
    
# Load user_info as a global variable

st.logo(image="logo/PhonoEcho.png", icon_image="logo/PhonoEcho.png")
st.markdown(
    """
    <style>
        div[data-testid="stSidebarHeader"] > img, div[data-testid="collapsedControl"] > img {
            height: 6rem;
            width: auto;
        }
        
        div[data-testid="stSidebarHeader"], div[data-testid="stSidebarHeader"] > *,
        div[data-testid="collapsedControl"], div[data-testid="collapsedControl"] > * {
            display: flex;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ! learning_data is very important! it will be used to reload the page
if "learning_data" not in st.session_state:
    st.session_state['learning_data'] = {
        'overall_score': None,
        'radar_chart': None,
        'waveform_plot': None,
        'error_table': None,
        'syllable_table': None
    }

def login():
    """Log in the current user."""
    _, cent_co, _ = st.columns([0.2, 0.7, 0.1])
    with cent_co:
        with open("logo/PhonoEcho.gif", "rb") as f:
            contents = f.read()
            data_url = base64.b64encode(contents).decode("utf-8")
        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="cat gif" class="center">',
            unsafe_allow_html=True,
        )
    st.markdown("# PhonoEchoへよこそう! 😍 発音を上達しましょう!")
    with st.form(key='password_form'):
        username = st.text_input("ユーザー名", key="username")
        password = st.text_input("パスワード", key="password", type="password")
        submit_button = st.form_submit_button(label='ログイン')

        if submit_button:
            user = User.login(username, password)
            if user:
                st.session_state.logged_in = True
                # !!!pass the user obj to any page!!!
                st.session_state.user = user
                global learning_page
                st.switch_page(learning_page)
            
def register():
    """Register the item."""
    _, cent_co, _ = st.columns([0.2, 0.7, 0.1])
    with cent_co:
        with open("logo/EchoLearn.gif", "rb") as f:
            contents = f.read()
            data_url = base64.b64encode(contents).decode("utf-8")
        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="cat gif" class="center">',
            unsafe_allow_html=True,
        )
    st.markdown("# 新規登録して利用できます! 😉")
    with st.form(key='register_form'):
        username = st.text_input("ユーザー名", key="username")
        password = st.text_input("パスワード", key="password", type="password")
        submit_button = st.form_submit_button(label='新規登録')

        if submit_button:
            user = User.register(username, password)
            if user:
                st.session_state.logged_in = True
                # !!!pass the user obj to any page!!!
                st.session_state.user = user
                global login_page
                st.switch_page(login_page)

def logout():
    # After logging out, delete all the keys of st.session_state
    """Log out the current user."""
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# Account-related Page
login_page = st.Page(login, title="ログイン", icon=":material/login:")
register_page = st.Page(register, title="新規登録", icon=":material/login:")
logout_page = st.Page(logout, title="ログアウト", icon=":material/logout:")

# Learning-related Page
learning_page = st.Page("../app/learn/echo_learning.py", title='フォノエコーラーニング', icon="🔥")
# chatbox_page = st.Page("../app/learn/chatbox.py", title="PhonoEcho Pronunciation Coach", icon="🚨")

# Set the navigation of sidebar
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "アカウント": [logout_page],
            "ラーニング": [learning_page],
        }
    )
else:
    pg = st.navigation(
        {
            "アカウント": [login_page, register_page]
        }
    )

# Set the header of sidebar and run the main page
st.sidebar.header("PhonoEchoへようこそ! 😊")
if st.session_state.logged_in:
    st.sidebar.markdown("まず、アバターとTactGloveの同期性を確認しましょう！")
    delay_time = st.sidebar.number_input(
        "TactGloveの振動提示を〇〇秒遅らせる：", value=0.3, placeholder="タイムラグがなくなるようにしてください（例：0.01~1.0秒）",
        min_value=0.01, max_value=1.0, step=0.01
    )
    # Store delay_time in session state for use in other pages
    st.session_state.delay_time = delay_time
    
pg.run()
