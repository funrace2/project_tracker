"""
Project Tracker - Authentication Views
로그인 및 회원가입 화면
"""

import streamlit as st
from db_manager import create_user, verify_user, get_user_by_email
import re
import extra_streamlit_components as stx
import hashlib


def get_cookie_manager():
    """쿠키 매니저 가져오기 (지연 초기화)"""
    return stx.CookieManager()


def create_auth_token(user_id: int, email: str) -> str:
    """
    인증 토큰 생성 (간단한 해시)

    Args:
        user_id: 사용자 ID
        email: 이메일

    Returns:
        str: 인증 토큰
    """
    # 간단한 토큰 생성 (실제 운영환경에서는 JWT 사용 권장)
    token_data = f"{user_id}:{email}:project_tracker_secret"
    return hashlib.sha256(token_data.encode()).hexdigest()[:32]


def save_login_cookie(user_id: int, email: str):
    """로그인 쿠키 저장"""
    cookie_manager = get_cookie_manager()
    token = create_auth_token(user_id, email)
    cookie_manager.set('auth_token', token, expires_at=None)  # 브라우저 종료 시까지 유지
    cookie_manager.set('user_id', str(user_id), expires_at=None)
    cookie_manager.set('user_email', email, expires_at=None)


def clear_login_cookie():
    """로그인 쿠키 삭제"""
    cookie_manager = get_cookie_manager()
    cookie_manager.delete('auth_token')
    cookie_manager.delete('user_id')
    cookie_manager.delete('user_email')


def check_auto_login():
    """
    쿠키 확인하여 자동 로그인

    Returns:
        dict: 사용자 정보 또는 None
    """
    try:
        cookie_manager = get_cookie_manager()
        cookies = cookie_manager.get_all()

        if not cookies or 'auth_token' not in cookies:
            return None

        user_id = cookies.get('user_id')
        user_email = cookies.get('user_email')
        auth_token = cookies.get('auth_token')

        if not user_id or not user_email or not auth_token:
            return None

        # 토큰 검증
        expected_token = create_auth_token(int(user_id), user_email)
        if auth_token != expected_token:
            clear_login_cookie()
            return None

        # 사용자 정보 가져오기
        user = get_user_by_email(user_email)
        if user and user['id'] == int(user_id):
            return user

        return None
    except:
        return None


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

                        # 쿠키에 로그인 정보 저장 (자동 로그인용)
                        save_login_cookie(user['id'], user['email'])

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

    # 자동 로그인 체크 (쿠키 확인)
    if not st.session_state.authenticated:
        user = check_auto_login()
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            st.rerun()

    # 회원가입 페이지 표시 여부
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        show_signup_page()
    else:
        show_login_page()


def logout():
    """로그아웃"""
    # 쿠키 삭제
    clear_login_cookie()

    # 세션 상태 초기화
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
