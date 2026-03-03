import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="פלטפורמת תחקור", layout="centered")

# פונקציית חיבור לגוגל שיטס
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    client = gspread.authorize(creds)
    return client.open("Psychometry_Platform").get_worksheet(0)

# בדיקה אם המשתמש כבר "נכנס" (בצורה פשוטה לבינתיים כדי לעקוף את השגיאה)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 כניסה למערכת")
    email = st.text_input("הכניסו מייל:")
    # סיסמה פשוטה שרק את ואופק/רותם תדעו (את יכולה לשנות אותה כאן)
    password = st.text_input("סיסמה:", type="password")
    
    if st.button("כניסה"):
        if email and password == "1234": # שנו את 1234 לסיסמה שתרצו
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("מייל או סיסמה שגויים")
else:
    # האפליקציה עצמה אחרי התחברות
    st.sidebar.write(f"שלום, {st.session_state.user_email}")
    if st.sidebar.button("התנתק"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("אתר תחקור")

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
                # שמירה לגיליון עם המייל של מי שנכנס
                sheet.append_row([st.session_state.user_email, section, st.session_state.q_num, i])
                st.toast(f"תשובה {i} נשמרה")
                st.session_state.q_num += 1

        if st.button("איפוס מונה"):
            st.session_state.q_num = 1
            st.rerun()
            
    except Exception as e:
        st.error(f"שגיאה בחיבור: {e}")
