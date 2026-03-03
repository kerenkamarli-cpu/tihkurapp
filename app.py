import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="פלטפורמת תחקור פסיכומטרי", layout="centered")
st.title("פלטפורמת תחקור")

def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # בדיקה אם המפתח קיים ב-Secrets
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        # אם זה טקסט (בגלל הגרשיים המרובעים), נהפוך אותו לדיקשנרי
        import json
        if isinstance(creds_info, str):
            creds_info = json.loads(creds_info)
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        # וודאי ששם הגיליון בדרייב הוא בדיוק Psychometry_Platform
        return client.open("Psychometry_Platform").get_worksheet(0)
    else:
        return None

try:
    sheet = get_gsheet()
    
    if sheet is None:
        st.error("לא נמצא מפתח ב-Secrets. וודאי שהגדרת 'gcp_service_account' ב-Streamlit Settings.")
    else:
        # ממשק האפליקציה
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
    st.error(f"שגיאת חיבור: {e}")
    st.info("וודאי שהגיליון משותף עם המייל של ה-Service Account ושהשם שלו תואם.")
