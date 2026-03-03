import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# הגדרות תצוגה
st.set_page_config(page_title="פלטפורמת תיחקור פסיכומטרי", layout="centered")

st.title("🎯 פלטפורמת התיחקור של קרו")

# חיבור לגוגל שיטס באמצעות ה-Secrets (הכספת)
def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # משיכת המפתח מהכספת של Streamlit
    creds_dict = st.secrets["gcp_service_account"] 
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # וודאי שהשם כאן תואם לשם הגיליון שלך
    return client.open("Psychometry_Platform").get_worksheet(0)

try:
    sheet = get_gsheet()
    
    # ממשק המשתמש
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.selectbox("מי מזין?", ["קרן", "אופק", "רותם", "אורח"])
    with col2:
        exam_date = st.selectbox("מועד המבחן:", ["אביב 2023", "סתיו 2023", "חורף 2024", "אחר"])

    section = st.radio("בחר פרק:", ["כמותי 1", "כמותי 2", "מילולי 1", "מילולי 2", "אנגלית 1", "אנגלית 2"], horizontal=True)

    if 'q_num' not in st.session_state:
        st.session_state.q_num = 1

    st.divider()
    st.write(f"### שאלה מספר: {st.session_state.q_num}")
    
    cols = st.columns(4)
    for i in range(1, 5):
        if cols[i-1].button(f"{i}", use_container_width=True, key=f"btn_{i}"):
            sheet.append_row([user_name, exam_date, section, st.session_state.q_num, i])
            st.toast(f"תשובה {i} נשמרה!", icon='✅')
            st.session_state.q_num += 1

    if st.button("איפוס מונה שאלות"):
        st.session_state.q_num = 1
        st.rerun()

except Exception as e:
    st.error("האפליקציה מחכה להזנת המפתח ב-Secrets...")
    st.info("היכנסי ל-Settings -> Secrets ב-Streamlit Cloud והדביקי את תוכן קובץ ה-creds.json.")
