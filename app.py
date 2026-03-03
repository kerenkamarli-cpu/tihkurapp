import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from streamlit_google_auth import Authenticate

st.set_page_config(page_title="פלטפורמת תיחקור", layout="centered")

# הגדרת התחברות גוגל
auth = Authenticate(
    secret_credentials_path=None, # אנחנו משתמשים ב-Secrets ולא בקובץ
    cookie_name='my_auth_cookie',
    key='auth_key',
    cookie_expiry_days=30,
    client_id=st.secrets["google_client_id"],
    client_secret=st.secrets["google_client_secret"],
    redirect_uri=st.secrets.get("redirect_uri", "https://tihkurapp.streamlit.app"),
)

# בדיקה אם המשתמש מחובר
auth.check_authenticity()

if st.session_state['connected']:
    # אם מחובר - הצגת האתר
    st.sidebar.write(f"מחובר כ: {st.session_state['user_info'].get('email')}")
    if st.sidebar.button("התנתק"):
        auth.logout()

    st.title("🎯 פלטפורמת התיחקור של קרן")

    def get_gsheet():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = json.loads(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        return client.open("Psychometry_Platform").get_worksheet(0)

    try:
        sheet = get_gsheet()
        section = st.radio("בחר פרק:", ["כמותי 1", "כמותי 2", "מילולי 1", "מילולי 2", "אנגלית 1", "אנגלית 2"], horizontal=True)

        if 'q_num' not in st.session_state:
            st.session_state.q_num = 1

        st.divider()
        st.write(f"### שאלה מספר: {st.session_state.q_num}")
        
        cols = st.columns(4)
        for i in range(1, 5):
            if cols[i-1].button(f"{i}", use_container_width=True, key=f"btn_{i}"):
                # שמירת נתונים: מייל המשתמש, פרק, מספר שאלה ותשובה
                user_email = st.session_state['user_info'].get('email')
                sheet.append_row([user_email, section, st.session_state.q_num, i])
                st.toast(f"תשובה {i} נשמרה")
                st.session_state.q_num += 1

        if st.button("איפוס מונה"):
            st.session_state.q_num = 1
            st.rerun()
            
    except Exception as e:
        st.error(f"שגיאה בחיבור לגיליון: {e}")

else:
    # אם לא מחובר - הצגת כפתור התחברות בלבד
    st.title("ברוכים הבאים לפלטפורמת התיחקור")
    st.info("אנא התחברו עם חשבון הגוגל שלכם כדי להמשיך")
    auth.login()
