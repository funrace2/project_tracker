"""
Project Tracker - Main Application
부트캠프 학생을 위한 프로젝트 관리 도구
"""

import streamlit as st
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go

# 로컬 모듈
import db_manager as db
import utils
from config import PAGE_CONFIG, APP_TITLE, PROJECT_STATUS


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


# ========================================
# 사이드바 - 프로젝트 관리
# ========================================

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


def show_create_project_form():
    """프로젝트 생성 폼"""

    st.subheader("➕ 새 프로젝트 만들기")

    with st.form("create_project_form"):
        name = st.text_input("프로젝트명*", max_chars=200, placeholder="예: 감정 일기 앱")
        description = st.text_area("설명", height=100, placeholder="프로젝트에 대한 간단한 설명")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date.today())
        with col2:
            target_end_date = st.date_input("목표 완료일", value=None)

        col_cancel, col_submit = st.columns(2)

        with col_cancel:
            cancel = st.form_submit_button("취소", use_container_width=True)
        with col_submit:
            submit = st.form_submit_button("생성", type="primary", use_container_width=True)

        if cancel:
            st.session_state.show_create_project = False
            st.rerun()

        if submit:
            # 입력 검증
            errors = utils.validate_project_input(name, start_date, target_end_date)

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # 프로젝트 생성
                project_id = db.insert_project(
                    name=name.strip(),
                    description=description.strip() if description else None,
                    start_date=start_date,
                    target_end_date=target_end_date
                )

                if project_id:
                    st.success(f"✅ '{name}' 프로젝트가 생성되었습니다!")
                    st.session_state.current_project_id = project_id
                    st.session_state.show_create_project = False
                    st.rerun()
                else:
                    st.error("프로젝트 생성에 실패했습니다.")


# ========================================
# 메인 컨텐츠
# ========================================

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

    # 프로젝트 헤더
    st.title(f"📋 {project['name']}")

    # 프로젝트 정보
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


# ========================================
# 대시보드 탭
# ========================================

def render_dashboard_tab(project):
    """대시보드 탭 렌더링"""

    st.subheader("📊 프로젝트 대시보드")

    # TODO: 대시보드 구현
    st.info("🚧 대시보드 기능은 다음 단계에서 구현됩니다.")


# ========================================
# Kanban 보드 탭
# ========================================

def render_kanban_tab(project):
    """Kanban 보드 탭 렌더링"""

    st.subheader("📋 Kanban 보드")

    # TODO: Kanban 보드 구현
    st.info("🚧 Kanban 보드 기능은 다음 단계에서 구현됩니다.")


# ========================================
# 회고 탭
# ========================================

def render_retrospective_tab(project):
    """회고 탭 렌더링"""

    st.subheader("📝 프로젝트 회고 (KPT)")

    # TODO: 회고 기능 구현
    st.info("🚧 회고 기능은 다음 단계에서 구현됩니다.")


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
