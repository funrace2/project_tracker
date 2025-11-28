"""
Project Tracker - Main Application
부트캠프 학생을 위한 프로젝트 관리 도구
"""

import streamlit as st
from config import PAGE_CONFIG

# Components
from components import (
    render_sidebar,
    show_create_project_form,
    render_main_content
)


# ========================================
# 페이지 설정
# ========================================

st.set_page_config(**PAGE_CONFIG)


# ========================================
# 세션 상태 초기화
# ========================================

if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None

if 'show_create_project' not in st.session_state:
    st.session_state.show_create_project = False

if 'show_create_task' not in st.session_state:
    st.session_state.show_create_task = False

if 'view_task_id' not in st.session_state:
    st.session_state.view_task_id = None

if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None

if 'edit_project_id' not in st.session_state:
    st.session_state.edit_project_id = None


# ========================================
# 메인 실행
# ========================================

def main():
    """메인 함수"""

    # 사이드바 렌더링
    render_sidebar()

    # 프로젝트 생성 폼 표시
    if st.session_state.show_create_project:
        show_create_project_form()
    else:
        # 메인 컨텐츠 렌더링
        render_main_content()


if __name__ == "__main__":
    main()
