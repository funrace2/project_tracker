"""
Project Tracker - Authentication Views
로그인 및 회원가입 화면
"""

import streamlit as st
from db_manager import create_user, verify_user, get_user_by_email
import re


def is_valid_email(email: str) -> bool:
    """
    이메일 형식 검증

    Args:
        email: 검증할 이메일

    Returns:
        bool: 유효하면 True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def show_login_page():
    """로그인 페이지 표시"""

    # 중앙 정렬을 위한 컬럼 레이아웃
    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        st.title("🔐 로그인")

        with st.form("login_form"):
            email = st.text_input("이메일", placeholder="example@email.com")
            password = st.text_input("비밀번호", type="password")

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                login_button = st.form_submit_button("로그인", use_container_width=True)
            with col_btn2:
                signup_button = st.form_submit_button("회원가입", use_container_width=True)

            if login_button:
                if not email or not password:
                    st.error("이메일과 비밀번호를 입력해주세요")
                else:
                    user = verify_user(email, password)
                    if user:
                        # 세션에 사용자 정보 저장
                        st.session_state.user = user
                        st.session_state.authenticated = True

                        st.success(f"환영합니다, {user['username']}님!")
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 올바르지 않습니다")

            if signup_button:
                st.session_state.show_signup = True
                st.rerun()


def show_signup_page():
    """회원가입 페이지 표시"""

    # 중앙 정렬을 위한 컬럼 레이아웃
    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        st.title("📝 회원가입")

        with st.form("signup_form"):
            username = st.text_input("이름", placeholder="홍길동")
            email = st.text_input("이메일", placeholder="example@email.com")
            password = st.text_input("비밀번호", type="password")
            password_confirm = st.text_input("비밀번호 확인", type="password")

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                signup_button = st.form_submit_button("가입하기", use_container_width=True)
            with col_btn2:
                back_button = st.form_submit_button("뒤로가기", use_container_width=True)

            if signup_button:
                # 입력 검증
                if not username or not email or not password:
                    st.error("모든 필드를 입력해주세요")
                elif not is_valid_email(email):
                    st.error("올바른 이메일 형식이 아닙니다")
                elif len(password) < 6:
                    st.error("비밀번호는 최소 6자 이상이어야 합니다")
                elif password != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다")
                else:
                    # 이메일 중복 체크
                    existing_user = get_user_by_email(email)
                    if existing_user:
                        st.error("이미 가입된 이메일입니다")
                    else:
                        # 회원가입 진행
                        user_id = create_user(email, password, username)
                        if user_id:
                            st.success("회원가입이 완료되었습니다! 로그인해주세요")
                            st.session_state.show_signup = False
                            st.rerun()
                        else:
                            st.error("회원가입 중 오류가 발생했습니다")

            if back_button:
                st.session_state.show_signup = False
                st.rerun()


def show_auth_page():
    """인증 페이지 (로그인 또는 회원가입)"""

    # 회원가입 페이지 표시 여부
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        show_signup_page()
    else:
        show_login_page()


def logout():
    """로그아웃"""
    # 세션 상태 초기화
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
