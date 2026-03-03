import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# כותרת נקייה
st.set_page_config(page_title="פלטפורמת תחקור", layout="centered")
st.title("תחקור")

def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds_info = json.loads(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        return client.open("Psychometry_Platform").get_worksheet(0)
    return None

# כאן יבוא בהמשך מנגנון ה-Login של גוגל
# כרגע האפליקציה תציג רק את כפתורי ההזנה
try:
    sheet = get_gsheet()
    if sheet:
        section = st.radio("בחר פרק:", ["כמותי 1", "כמותי 2", "מילולי 1", "מילולי 2", "אנגלית 1", "אנגלית 2"], horizontal=True)

        if 'q_num' not in st.session_state:
            st.session_state.q_num = 1

        st.divider()
        st.write(f"### שאלה מספר: {st.session_state.q_num}")
        
        cols = st.columns(4)
        for i in range(1, 5):
            if cols[i-1].button(f"{i}", use_container_width=True, key=f"btn_{i}"):
                # שומר רק פרק, מספר שאלה ותשובה
                sheet.append_row([section, st.session_state.q_num, i])
                st.toast(f"שאלה {st.session_state.q_num}: תשובה {i} נשמרה")
                st.session_state.q_num += 1

        if st.button("איפוס"):
            st.session_state.q_num = 1
            st.rerun()
except Exception as e:
    st.error(f"שגיאה: {e}")
