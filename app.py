import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
import os
from quiz_core import *
import base64

# ຕັ້ງຄ່າໜ້າ
st.set_page_config(
    page_title="Quiz System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ໂຫລດ CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ສ້າງ session state ສຳລັບເກັບຂໍ້ມູນຜູ້ໃຊ້
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# ຫົວຂໍ້ຫຼັກ
st.markdown("""
    <div class="main-header">
        <h1>📝 ລະບົບຈັດການຂໍ້ສອບອັດສະລິຍະ</h1>
        <p>ຮຽນຮູ້ ທົດສອບ ແລະ ພັດທະນາຕົນເອງໄປກັບພວກເຮົາ</p>
    </div>
""", unsafe_allow_html=True)

# ໜ້າເຂົ້າສູ່ລະບົບ
if st.session_state.current_page == 'login':
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.subheader("🔐 ເຂົ້າສູ່ລະບົບ")

        role = st.radio("ເລືອກບົດບາດ:", ["ນັກຮຽນ", "ຄູ/ຜູ້ດູແລ"])

        if role == "ນັກຮຽນ":
            student_id = st.text_input("ລະຫັດນັກຮຽນ:", placeholder="ຕົວຢ່າງ: 65010123")
            if st.button("ເຂົ້າສູ່ລະບົບ", use_container_width=True):
                if student_id:
                    st.session_state.user_role = 'student'
                    st.session_state.user_id = student_id
                    st.session_state.current_page = 'student_dashboard'
                    st.rerun()
                else:
                    st.error("ກະລຸນາປ້ອນລະຫັດນັກຮຽນ")

        else:  # ຄູ
            teacher_id = st.text_input("ຊື່ຜູ້ໃຊ້:", placeholder="admin")
            teacher_pass = st.text_input("ລະຫັດຜ່ານ:", type="password")
            if st.button("ເຂົ້າສູ່ລະບົບ", use_container_width=True):
                # ກວດສອບແບບງ່າຍໆ (ສາມາດປ່ຽນເປັນການກວດສອບຈາກ Google Sheet ກໍໄດ້)
                if teacher_id == "admin" and teacher_pass == "admin123":
                    st.session_state.user_role = 'teacher'
                    st.session_state.user_id = teacher_id
                    st.session_state.current_page = 'teacher_dashboard'
                    st.rerun()
                else:
                    st.error("ຊື່ຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ")
        st.markdown('</div>', unsafe_allow_html=True)

# ໜ້າຫຼັກຂອງນັກຮຽນ
elif st.session_state.current_page == 'student_dashboard':
    # Sidebar ສຳລັບນັກຮຽນ
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Student", width=150)
        st.markdown(f"### 👤 {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🏠 ໜ້າຫຼັກ", use_container_width=True):
            st.session_state.current_page = 'student_dashboard'
            st.rerun()
        if st.button("📊 ປະຫວັດການສອບ", use_container_width=True):
            st.session_state.current_page = 'student_history'
            st.rerun()
        if st.button("🚪 ອອກຈາກລະບົບ", use_container_width=True):
            for key in ['user_role', 'user_id', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ເນື້ອຫາຫຼັກ
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.subheader(f"ສະບາຍດີ, ນັກຮຽນ {st.session_state.user_id}")

    # ສະແດງຊຸດຂໍ້ສອບທີ່ມີ
    quiz_sets = get_quiz_sets()
    if not quiz_sets:
        st.warning("ຍັງບໍ່ມີຊຸດຂໍ້ສອບໃນລະບົບ")
    else:
        st.markdown("### ເລືອກຊຸດຂໍ້ສອບທີ່ທ່ານຕ້ອງການເຮັດ")

        # ສະແດງເປັນກຣດ
        cols = st.columns(3)
        for i, quiz in enumerate(quiz_sets):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 1.5rem; border-radius: 10px; color: white;
                                text-align: center; margin: 0.5rem 0;">
                        <h3>{quiz}</h3>
                        <p>ຈຳນວນຂໍ້: {len(load_questions(quiz))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"ເລີ່ມເຮັດ {quiz}", key=f"start_{quiz}"):
                        st.session_state.selected_quiz = quiz
                        st.session_state.current_page = 'take_quiz'
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ໜ້າເຮັດຂໍ້ສອບ
elif st.session_state.current_page == 'take_quiz':
    # ກວດສອບວ່າມີການເລືອກຊຸດຂໍ້ສອບແລ້ວ
    if 'selected_quiz' not in st.session_state:
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

    # ໂຫລດຂໍ້ມູນຂໍ້ສອບ
    if 'quiz_questions' not in st.session_state:
        questions = load_questions(st.session_state.selected_quiz)
        st.session_state.quiz_questions = questions
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.answers = {}
        st.session_state.start_time = time.time()
        st.session_state.time_limit = 10 * 60  # 10 ນາທີ

    questions = st.session_state.quiz_questions
    total = len(questions)
    idx = st.session_state.current_q

    # ຄຳນວນເວລາທີ່ເຫຼືອ
    elapsed = time.time() - st.session_state.start_time
    remaining = st.session_state.time_limit - elapsed

    # ກວດສອບວ່າໝົດເວລາຫຼືບໍ່
    if remaining <= 0:
        st.warning("⏰ ໝົດເວລາ! ກຳລັງບັນທຶກຜົນ...")
        save_result(
            st.session_state.user_id,
            st.session_state.selected_quiz,
            st.session_state.score,
            total,
            st.session_state.answers
        )
        # ລຶບ session state ທີ່ກ່ຽວຂ້ອງກັບການສອບ
        for key in ['quiz_questions', 'current_q', 'score', 'answers', 'start_time', 'time_limit', 'selected_quiz']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_page = 'student_dashboard'
        st.rerun()

    # ສະແດງເວລາ
    mins, secs = divmod(int(remaining), 60)
    time_str = f"{mins:02d}:{secs:02d}"
    st.markdown(f'<div class="timer-box">⏳ ເວລາເຫຼືອ: {time_str}</div>', unsafe_allow_html=True)

    # ສະແດງຄວາມຄືບໜ້າ
    st.progress((idx) / total, text=f"ຂໍ້ທີ {idx+1}/{total}")

    # ສະແດງຄະແນນປັດຈຸບັນ
    st.markdown(f'<div class="score-badge">ຄະແນນ: {st.session_state.score}</div>', unsafe_allow_html=True)

    if idx < total:
        q = questions[idx]
        st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
        st.markdown(f"### {q['Question']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # ສ້າງຕົວເລືອກ
        options = {
            'A': q['OptionA'],
            'B': q['OptionB'],
            'C': q['OptionC'],
            'D': q['OptionD']
        }

        # ໃຊ້ radio ທີ່ສວຍງາມ
        answer = st.radio(
            "ເລືອກຄຳຕອບ:",
            options.keys(),
            format_func=lambda x: f"{x}. {options[x]}",
            key=f"q_{idx}",
            horizontal=True
        )

        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("✅ ສົ່ງຄຳຕອບ", use_container_width=True):
                correct = q['CorrectAnswer']
                is_correct = (answer == correct)

                if is_correct:
                    st.session_state.score += 1
                    st.markdown('<div class="success-message">✅ ຖືກຕ້ອງ!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-message">❌ ຜິດ ຄຳຕອບທີ່ຖືກແມ່ນ {correct}</div>', unsafe_allow_html=True)

                st.session_state.answers[str(q['ID'])] = answer
                st.session_state.current_q += 1
                time.sleep(1)  # ໃຫ້ເຫັນຂໍ້ຄວາມກ່ອນປ່ຽນຂໍ້
                st.rerun()

    # ຖ້າເຮັດຄົບທຸກຂໍ້
    if st.session_state.current_q >= total:
        st.balloons()
        st.markdown('<div class="success-message">🎉 ເຮັດຂໍ້ສອບສຳເລັດ!</div>', unsafe_allow_html=True)
        st.markdown(f"## ທ່ານໄດ້ {st.session_state.score}/{total} ຄະແນນ")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 ບັນທຶກຜົນ", use_container_width=True):
                save_result(
                    st.session_state.user_id,
                    st.session_state.selected_quiz,
                    st.session_state.score,
                    total,
                    st.session_state.answers
                )
                # ລຶບ session state
                for key in ['quiz_questions', 'current_q', 'score', 'answers', 'start_time', 'time_limit', 'selected_quiz']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = 'student_dashboard'
                st.rerun()
        with col2:
            if st.button("🏠 ກັບໜ້າຫຼັກ", use_container_width=True):
                for key in ['quiz_questions', 'current_q', 'score', 'answers', 'start_time', 'time_limit', 'selected_quiz']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = 'student_dashboard'
                st.rerun()

# ໜ້າປະຫວັດການສອບຂອງນັກຮຽນ
elif st.session_state.current_page == 'student_history':
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Student", width=150)
        st.markdown(f"### 👤 {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🏠 ໜ້າຫຼັກ", use_container_width=True):
            st.session_state.current_page = 'student_dashboard'
            st.rerun()
        if st.button("📊 ປະຫວັດການສອບ", use_container_width=True):
            pass
        if st.button("🚪 ອອກຈາກລະບົບ", use_container_width=True):
            for key in ['user_role', 'user_id', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.subheader("📊 ປະຫວັດການເຮັດຂໍ້ສອບ")

    # ດຶງຂໍ້ມູນຈາກ Google Sheet
    records = responses_sheet.get_all_records()
    student_records = [r for r in records if str(r['StudentID']) == str(st.session_state.user_id)]

    if not student_records:
        st.info("ທ່ານຍັງບໍ່ເຄີຍເຮັດຂໍ້ສອບໃດໆ")
    else:
        # ສະແດງເປັນ DataFrame
        df = pd.DataFrame(student_records)
        df = df[['Timestamp', 'QuizSet', 'Score', 'Total']]
        df['Percent'] = (df['Score'] / df['Total'] * 100).round(1)
        df['Percent'] = df['Percent'].astype(str) + '%'

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": "ວັນທີ",
                "QuizSet": "ຊຸດຂໍ້ສອບ",
                "Score": "ຄະແນນ",
                "Total": "ຈຳນວນຂໍ້",
                "Percent": "%"
            }
        )

        # ສະແດງສະຖິຕິ
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ຈຳນວນຄັ້ງທີ່ເຮັດ", len(student_records))
        with col2:
            avg_score = df['Score'].mean()
            st.metric("ຄະແນນສະເລ່ຍ", f"{avg_score:.1f}")
        with col3:
            avg_percent = (df['Score'].sum() / df['Total'].sum() * 100) if df['Total'].sum() > 0 else 0
            st.metric("% ສະເລ່ຍ", f"{avg_percent:.1f}%")

        # ປຸ່ມສ້າງ PDF
        if st.button("📄 ສ້າງລາຍງານ PDF", use_container_width=True):
            filename = generate_student_report(st.session_state.user_id)
            if filename and os.path.exists(filename):
                with open(filename, "rb") as f:
                    bytes_data = f.read()
                b64 = base64.b64encode(bytes_data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filename)}">ດາວໂຫລດລາຍງານ PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("ບໍ່ສາມາດສ້າງລາຍງານໄດ້")

    st.markdown('</div>', unsafe_allow_html=True)

# ໜ້າຫຼັກຂອງຄູ
elif st.session_state.current_page == 'teacher_dashboard':
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Teacher", width=150)
        st.markdown(f"### 👤 ຄູ {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🏠 ໜ້າຫຼັກ", use_container_width=True):
            st.session_state.current_page = 'teacher_dashboard'
            st.rerun()
        if st.button("📊 ເບິ່ງຜົນການສອບ", use_container_width=True):
            st.session_state.current_page = 'teacher_results'
            st.rerun()
        if st.button("📄 ສ້າງລາຍງານ", use_container_width=True):
            st.session_state.current_page = 'teacher_reports'
            st.rerun()
        if st.button("🚪 ອອກຈາກລະບົບ", use_container_width=True):
            for key in ['user_role', 'user_id', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.subheader("👨‍🏫 ແຜງຄວບຄຸມສຳລັບຄູ")

    st.markdown("""
    <div class="info-box">
        <h4>ຍິນດີຕ້ອນຮັບຄູຜູ້ດູແລລະບົບ</h4>
        <p>ທ່ານສາມາດຈັດການຂໍ້ມູນຜ່ານ Google Sheets ໂດຍກົງ ຫຼື ໃຊ້ເຄື່ອງມືໃນແຖບດ້ານຂ້າງ</p>
    </div>
    """, unsafe_allow_html=True)

    # ສະແດງສະຖິຕິລວມ
    records = responses_sheet.get_all_records()
    if records:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ນັກຮຽນທັງໝົດ", len(set(r['StudentID'] for r in records)))
        with col2:
            st.metric("ຈຳນວນຄັ້ງທີ່ສອບ", len(records))
        with col3:
            st.metric("ຊຸດຂໍ້ສອບ", len(get_quiz_sets()))
        with col4:
            avg_score = sum(r['Score'] for r in records) / len(records) if records else 0
            st.metric("ຄະແນນສະເລ່ຍ", f"{avg_score:.1f}")

    st.markdown('</div>', unsafe_allow_html=True)

# ໜ້າເບິ່ງຜົນການສອບ (ສຳລັບຄູ)
elif st.session_state.current_page == 'teacher_results':
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Teacher", width=150)
        st.markdown(f"### 👤 ຄູ {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🏠 ໜ້າຫຼັກ", use_container_width=True):
            st.session_state.current_page = 'teacher_dashboard'
            st.rerun()
        if st.button("📊 ເບິ່ງຜົນການສອບ", use_container_width=True):
            pass
        if st.button("📄 ສ້າງລາຍງານ", use_container_width=True):
            st.session_state.current_page = 'teacher_reports'
            st.rerun()
        if st.button("🚪 ອອກຈາກລະບົບ", use_container_width=True):
            for key in ['user_role', 'user_id', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.subheader("📊 ຜົນການສອບຂອງນັກຮຽນທັງໝົດ")

    records = responses_sheet.get_all_records()
    if not records:
        st.info("ຍັງບໍ່ມີຂໍ້ມູນການສອບ")
    else:
        df = pd.DataFrame(records)
        df['Percent'] = (df['Score'] / df['Total'] * 100).round(1).astype(str) + '%'

        # ການກັ່ນຕອງ
        col1, col2 = st.columns(2)
        with col1:
            quiz_sets = ['ທັງໝົດ'] + get_quiz_sets()
            selected_quiz = st.selectbox("ກັ່ນຕອງຕາມຊຸດຂໍ້ສອບ:", quiz_sets)
        with col2:
            if selected_quiz != 'ທັງໝົດ':
                df = df[df['QuizSet'] == selected_quiz]

        # ສະແດງຕາຕະລາງ
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": "ວັນທີ",
                "StudentID": "ລະຫັດນັກຮຽນ",
                "QuizSet": "ຊຸດຂໍ້ສອບ",
                "Score": "ຄະແນນ",
                "Total": "ຈຳນວນຂໍ້",
                "Percent": "%",
                "Details": "ລາຍລະອຽດ"
            }
        )

        # ສົ່ງອອກ CSV
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="quiz_results.csv">ດາວໂຫລດ CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ໜ້າສ້າງລາຍງານ PDF (ສຳລັບຄູ)
elif st.session_state.current_page == 'teacher_reports':
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Teacher", width=150)
        st.markdown(f"### 👤 ຄູ {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🏠 ໜ້າຫຼັກ", use_container_width=True):
            st.session_state.current_page = 'teacher_dashboard'
            st.rerun()
        if st.button("📊 ເບິ່ງຜົນການສອບ", use_container_width=True):
            st.session_state.current_page = 'teacher_results'
            st.rerun()
        if st.button("📄 ສ້າງລາຍງານ", use_container_width=True):
            pass
        if st.button("🚪 ອອກຈາກລະບົບ", use_container_width=True):
            for key in ['user_role', 'user_id', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.subheader("📄 ສ້າງລາຍງານ PDF")

    tab1, tab2 = st.tabs(["ລາຍງານສ່ວນບຸກຄົນ", "ລາຍງານລວມຫ້ອງ"])

    with tab1:
        st.markdown("### ສ້າງລາຍງານສຳລັບນັກຮຽນ")
        student_id = st.text_input("ປ້ອນລະຫັດນັກຮຽນ:", key="student_id_report")
        quiz_sets = ['ທັງໝົດ'] + get_quiz_sets()
        selected_quiz = st.selectbox("ເລືອກຊຸດຂໍ້ສອບ (ເລືອກທັງໝົດ ຫາກຕ້ອງການທຸກຊຸດ):", quiz_sets, key="quiz_select")

        if st.button("ສ້າງລາຍງານ", key="gen_student"):
            if student_id:
                quiz_param = None if selected_quiz == 'ທັງໝົດ' else selected_quiz
                filename = generate_student_report(student_id, quiz_param)
                if filename and os.path.exists(filename):
                    with open(filename, "rb") as f:
                        bytes_data = f.read()
                    b64 = base64.b64encode(bytes_data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filename)}">ດາວໂຫລດລາຍງານ PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("ບໍ່ພົບຂໍ້ມູນຂອງນັກຮຽນນີ້")
            else:
                st.warning("ກະລຸນາປ້ອນລະຫັດນັກຮຽນ")

    with tab2:
        st.markdown("### ສ້າງລາຍງານລວມຫ້ອງ")
        quiz_sets2 = ['ທັງໝົດ'] + get_quiz_sets()
        selected_quiz2 = st.selectbox("ເລືອກຊຸດຂໍ້ສອບ:", quiz_sets2, key="quiz_select2")

        if st.button("ສ້າງລາຍງານລວມ", key="gen_class"):
            quiz_param = None if selected_quiz2 == 'ທັງໝົດ' else selected_quiz2
            filename = generate_class_report(quiz_param)
            if filename and os.path.exists(filename):
                with open(filename, "rb") as f:
                    bytes_data = f.read()
                b64 = base64.b64encode(bytes_data).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(filename)}">ດາວໂຫລດລາຍງານ PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("ບໍ່ສາມາດສ້າງລາຍງານໄດ້ ຫຼື ບໍ່ມີຂໍ້ມູນ")

    st.markdown('</div>', unsafe_allow_html=True)
