"""
Project Tracker - Project Forms Component
프로젝트 생성/수정 폼
"""

import streamlit as st
from datetime import date
import db_manager as db
import utils


def show_create_project_form():
    """프로젝트 생성 폼"""

    st.subheader("➕ 새 프로젝트 만들기")

    with st.form("create_project_form"):
        name = st.text_input("프로젝트명*", max_chars=200, placeholder="예: 감정 일기 앱")
        description = st.text_area("설명", height=100, placeholder="프로젝트에 대한 간단한 설명")
        github_url = st.text_input(
            "GitHub URL",
            max_chars=500,
            placeholder="예: https://github.com/username/repository"
        )

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
                # 프로젝트 생성 (현재 로그인한 사용자의 ID 포함)
                user_id = st.session_state.user['id'] if st.session_state.user else None
                project_id = db.insert_project(
                    name=name.strip(),
                    description=description.strip() if description else None,
                    github_url=github_url.strip() if github_url else None,
                    start_date=start_date,
                    target_end_date=target_end_date,
                    user_id=user_id
                )

                if project_id:
                    st.success(f"✅ '{name}' 프로젝트가 생성되었습니다!")
                    st.session_state.current_project_id = project_id
                    st.session_state.show_create_project = False
                    st.rerun()
                else:
                    st.error("프로젝트 생성에 실패했습니다.")


@st.dialog("프로젝트 수정", width="large")
def show_edit_project_dialog(project):
    """프로젝트 수정 다이얼로그"""

    # 삭제 확인 모드
    if st.session_state.get('confirm_delete_project'):
        st.error("⚠️ 정말로 이 프로젝트를 삭제하시겠습니까?")
        st.warning("프로젝트의 모든 태스크와 데이터가 함께 삭제됩니다!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("취소", use_container_width=True, type="secondary"):
                st.session_state.confirm_delete_project = False
                st.rerun()
        with col2:
            if st.button("🗑️ 삭제 확인", type="primary", use_container_width=True):
                if db.delete_project(project['id']):
                    st.success("프로젝트가 삭제되었습니다.")
                    st.session_state.current_project_id = None
                    st.session_state.edit_project_id = None
                    st.session_state.confirm_delete_project = False
                    st.rerun()
                else:
                    st.error("프로젝트 삭제에 실패했습니다.")
        return

    st.subheader("✏️ 프로젝트 정보 수정")

    with st.form("edit_project_form"):
        name = st.text_input(
            "프로젝트명*",
            value=project['name'],
            max_chars=200,
            placeholder="예: 감정 일기 앱"
        )
        description = st.text_area(
            "설명",
            value=project.get('description') or '',
            height=100,
            placeholder="프로젝트에 대한 간단한 설명"
        )
        github_url = st.text_input(
            "GitHub URL",
            value=project.get('github_url') or '',
            max_chars=500,
            placeholder="예: https://github.com/username/repository"
        )

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "시작일",
                value=project['start_date'] if project.get('start_date') else date.today()
            )
        with col2:
            target_end_date = st.date_input(
                "목표 완료일",
                value=project['target_end_date'] if project.get('target_end_date') else None
            )

        # 상태 선택
        status_options = ['active', 'completed', 'on_hold']
        status_labels = {
            'active': '🔄 진행중',
            'completed': '✅ 완료',
            'on_hold': '⏸️ 보류'
        }
        current_status_index = status_options.index(project['status'])
        status = st.selectbox(
            "상태",
            options=status_options,
            format_func=lambda x: status_labels[x],
            index=current_status_index
        )

        col_cancel, col_submit, col_delete = st.columns(3)

        with col_cancel:
            cancel = st.form_submit_button("취소", use_container_width=True)
        with col_submit:
            submit = st.form_submit_button("저장", type="primary", use_container_width=True)
        with col_delete:
            delete = st.form_submit_button("🗑️ 삭제", use_container_width=True)

        if cancel:
            st.session_state.edit_project_id = None
            st.rerun()

        if delete:
            # 삭제 확인 모드로 전환
            st.session_state.confirm_delete_project = True
            st.rerun()

        if submit:
            # 입력 검증
            errors = utils.validate_project_input(name, start_date, target_end_date)

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # 프로젝트 수정
                success = db.update_project(
                    project['id'],
                    name=name.strip(),
                    description=description.strip() if description else None,
                    github_url=github_url.strip() if github_url else None,
                    start_date=start_date,
                    target_end_date=target_end_date,
                    status=status
                )

                if success:
                    st.success(f"✅ '{name}' 프로젝트가 수정되었습니다!")
                    st.session_state.edit_project_id = None
                    st.rerun()
                else:
                    st.error("프로젝트 수정에 실패했습니다.")
