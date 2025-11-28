"""
Project Tracker - Main Content Component
메인 컨텐츠 영역 렌더링
"""

import streamlit as st
import db_manager as db
import utils
from config import PROJECT_STATUS
from components.project_forms import show_edit_project_dialog
from views import render_dashboard_tab, render_kanban_tab, render_retrospective_tab


def render_main_content():
    """메인 컨텐츠 렌더링"""

    # 프로젝트가 선택되지 않은 경우
    if not st.session_state.current_project_id:
        st.info("👈 왼쪽 사이드바에서 프로젝트를 선택하거나 새로 만들어주세요.")
        return

    # 현재 프로젝트 정보
    project = db.get_project(st.session_state.current_project_id)

    if not project:
        st.error("프로젝트를 찾을 수 없습니다.")
        st.session_state.current_project_id = None
        return

    # 프로젝트 헤더 렌더링
    _render_project_header(project)

    # 프로젝트 정보 렌더링
    _render_project_info(project)

    if project.get('description'):
        with st.expander("📝 프로젝트 설명"):
            st.write(project['description'])

    st.markdown("---")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 대시보드", "📋 Kanban 보드", "📝 회고"])

    with tab1:
        render_dashboard_tab(project)

    with tab2:
        render_kanban_tab(project)

    with tab3:
        render_retrospective_tab(project)

    # 프로젝트 수정 다이얼로그
    if st.session_state.edit_project_id == project['id']:
        show_edit_project_dialog(project)


def _render_project_header(project):
    """프로젝트 헤더 렌더링 (제목, GitHub 버튼, 수정 버튼)"""

    if project.get('github_url'):
        header_col1, header_col2, header_col3 = st.columns([3, 1.2, 0.8])

        with header_col1:
            st.title(f"📋 {project['name']}")

        with header_col2:
            _render_github_button(project['github_url'])

        with header_col3:
            if st.button("✏️ 수정", use_container_width=True):
                st.session_state.edit_project_id = project['id']
                st.rerun()
    else:
        header_col1, header_col2 = st.columns([4, 1])

        with header_col1:
            st.title(f"📋 {project['name']}")

        with header_col2:
            if st.button("✏️ 수정", use_container_width=True):
                st.session_state.edit_project_id = project['id']
                st.rerun()


def _render_github_button(github_url):
    """GitHub 스타일 버튼 렌더링"""

    # GitHub URL에서 레포명 추출
    repo_name = github_url.rstrip('/').split('/')[-1]

    # GitHub 스타일 버튼
    st.markdown(
        f"""
        <a href="{github_url}" target="_blank" style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            background-color: #24292e;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            font-size: 14px;
            width: 100%;
            gap: 6px;
            transition: background-color 0.2s;
        ">
            <svg height="16" width="16" viewBox="0 0 16 16" fill="white" style="flex-shrink: 0;">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{repo_name}</span>
        </a>
        <style>
            a[href*="github.com"]:hover {{
                background-color: #2f363d !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


def _render_project_info(project):
    """프로젝트 정보 렌더링 (기간, 상태, 남은 기간)"""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("📅 기간")
        date_range = utils.get_date_range_text(project['start_date'], project['target_end_date'])
        st.write(date_range)

    with col2:
        st.caption("📊 상태")
        st.write(PROJECT_STATUS.get(project['status'], project['status']))

    with col3:
        if project.get('target_end_date'):
            days_left = utils.days_until(project['target_end_date'])
            st.caption("⏰ 남은 기간")
            if days_left > 0:
                st.write(f"{days_left}일")
            elif days_left == 0:
                st.write("🔥 D-Day")
            else:
                st.write(f"D+{abs(days_left)} (완료)")
