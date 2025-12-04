"""
Project Tracker - Sidebar Component
사이드바 렌더링 (프로젝트 관리)
"""

import streamlit as st
import db_manager as db
import utils
from config import APP_TITLE
from views import logout


def render_sidebar():
    """사이드바 렌더링 (프로젝트 선택 및 관리)"""

    with st.sidebar:
        st.title(APP_TITLE)

        # 사용자 정보 및 로그아웃
        if st.session_state.user:
            st.caption(f"👤 {st.session_state.user['username']}")
            if st.button("🚪 로그아웃", use_container_width=True):
                logout()

        st.markdown("---")

        # 새 프로젝트 버튼
        if st.button("➕ 새 프로젝트", use_container_width=True):
            st.session_state.show_create_project = True

        st.markdown("---")

        # 프로젝트 목록
        st.subheader("📋 프로젝트")

        # 현재 로그인한 사용자의 프로젝트만 조회
        user_id = st.session_state.user['id'] if st.session_state.user else None
        projects = db.get_projects(status='active', user_id=user_id)

        if not projects:
            st.info("프로젝트가 없습니다.\n새 프로젝트를 만들어보세요!")
        else:
            for project in projects:
                # 진행률 계산
                tasks = db.get_tasks(project['id'])
                metrics = utils.calculate_project_metrics(tasks)

                # 프로젝트 버튼
                if st.button(
                    project['name'],
                    key=f"project_{project['id']}",
                    use_container_width=True,
                    type="primary" if st.session_state.current_project_id == project['id'] else "secondary"
                ):
                    st.session_state.current_project_id = project['id']
                    st.rerun()

                # 진행률 및 마지막 업데이트
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📊 {metrics['progress_rate']:.0f}% 완료")
                with col2:
                    if project.get('updated_at'):
                        relative_time = utils.get_relative_time(project['updated_at'])
                        st.caption(f"🕐 {relative_time}")

        st.markdown("---")

        # 완료된 프로젝트 표시
        completed_projects = db.get_projects(status='completed', user_id=user_id)
        if completed_projects:
            with st.expander("✅ 완료된 프로젝트"):
                for project in completed_projects:
                    st.write(f"- {project['name']}")
