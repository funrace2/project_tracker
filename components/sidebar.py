"""
Project Tracker - Sidebar Component
사이드바 렌더링 (프로젝트 관리)
"""

import streamlit as st
import db_manager as db
import utils
from config import APP_TITLE


def render_sidebar():
    """사이드바 렌더링 (프로젝트 선택 및 관리)"""

    with st.sidebar:
        st.title(APP_TITLE)
        st.markdown("---")

        # 새 프로젝트 버튼
        if st.button("➕ 새 프로젝트", use_container_width=True):
            st.session_state.show_create_project = True

        st.markdown("---")

        # 프로젝트 목록
        st.subheader("📋 프로젝트")

        projects = db.get_projects(status='active')

        if not projects:
            st.info("프로젝트가 없습니다.\n새 프로젝트를 만들어보세요!")
        else:
            for project in projects:
                # 진행률 계산
                tasks = db.get_tasks(project['id'])
                metrics = utils.calculate_project_metrics(tasks)

                # 프로젝트 버튼
                button_label = f"{project['name']}\n{metrics['progress_rate']:.0f}% 완료"

                if st.button(
                    button_label,
                    key=f"project_{project['id']}",
                    use_container_width=True,
                    type="primary" if st.session_state.current_project_id == project['id'] else "secondary"
                ):
                    st.session_state.current_project_id = project['id']
                    st.rerun()

                # 마지막 업데이트
                if project.get('updated_at'):
                    relative_time = utils.get_relative_time(project['updated_at'])
                    st.caption(f"🕐 {relative_time}")

        st.markdown("---")

        # 완료된 프로젝트 표시
        completed_projects = db.get_projects(status='completed')
        if completed_projects:
            with st.expander("✅ 완료된 프로젝트"):
                for project in completed_projects:
                    st.write(f"- {project['name']}")
