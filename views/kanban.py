"""
Project Tracker - Kanban Board View
Kanban 보드 탭 렌더링
"""

import streamlit as st
import db_manager as db
import utils


def render_kanban_tab(project):
    """Kanban 보드 탭 렌더링"""

    project_id = project['id']

    # 빠른 태스크 추가
    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            quick_task_title = st.text_input(
                "빠른 추가",
                placeholder="태스크 제목을 입력하고 Enter를 누르세요...",
                label_visibility="collapsed",
                key="quick_task_input"
            )

        with col2:
            add_button = st.button("➕ 추가", use_container_width=True, key="quick_add_btn")

        if add_button and quick_task_title:
            task_id = db.insert_task(
                project_id=project_id,
                title=quick_task_title.strip(),
                status='todo',
                priority='medium'
            )

            if task_id:
                st.success(f"✅ 태스크가 추가되었습니다!")
                st.rerun()
            else:
                st.error("태스크 추가에 실패했습니다.")

    st.markdown("---")

    # 태스크 불러오기
    all_tasks = db.get_tasks(project_id)

    # 상태별로 분류
    todo_tasks = [t for t in all_tasks if t['status'] == 'todo']
    in_progress_tasks = [t for t in all_tasks if t['status'] == 'in_progress']
    done_tasks = [t for t in all_tasks if t['status'] == 'done']

    # 3개 컬럼 레이아웃
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📝 To Do")
        st.caption(f"{len(todo_tasks)}개")
        st.markdown("---")
        for task in todo_tasks:
            render_task_card(task, project_id)

    with col2:
        st.markdown("### 🔄 In Progress")
        st.caption(f"{len(in_progress_tasks)}개")
        st.markdown("---")
        for task in in_progress_tasks:
            render_task_card(task, project_id)

    with col3:
        st.markdown("### ✅ Done")
        st.caption(f"{len(done_tasks)}개")
        st.markdown("---")
        for task in done_tasks:
            render_task_card(task, project_id)

    # 태스크가 없는 경우
    if not all_tasks:
        st.info("📝 태스크가 없습니다. 위에서 첫 태스크를 추가해보세요!")


def render_task_card(task, project_id):
    """태스크 카드 렌더링"""

    with st.container():
        # 제목
        st.markdown(f"**{task['title']}**")

        # 메타 정보
        meta_info = []

        # 태그
        if task.get('tags'):
            tag_icon = utils.get_tag_icon(task['tags'])
            meta_info.append(tag_icon)

        # 우선순위
        priority_badge = utils.get_priority_badge(task['priority'])
        meta_info.append(priority_badge)

        if meta_info:
            st.caption(" | ".join(meta_info))

        # 마감일
        if task.get('due_date'):
            due_badge = utils.get_due_date_badge(task['due_date'])
            st.caption(due_badge)

        # 액션 버튼
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            if st.button("👁️", key=f"view_{task['id']}", help="상세보기"):
                st.session_state.view_task_id = task['id']
                st.rerun()

        with btn_col2:
            # 상태 변경 버튼
            if task['status'] == 'todo':
                if st.button("▶️", key=f"status_{task['id']}", help="진행 시작"):
                    db.update_task_status(task['id'], 'in_progress')
                    st.rerun()
            elif task['status'] == 'in_progress':
                if st.button("✅", key=f"status_{task['id']}", help="완료"):
                    db.update_task_status(task['id'], 'done')
                    st.rerun()
            elif task['status'] == 'done':
                if st.button("↩️", key=f"status_{task['id']}", help="다시 진행중으로"):
                    db.update_task_status(task['id'], 'in_progress')
                    st.rerun()

        with btn_col3:
            if st.button("🗑️", key=f"delete_{task['id']}", help="삭제"):
                if db.delete_task(task['id']):
                    st.success("태스크가 삭제되었습니다.")
                    st.rerun()

        st.markdown("---")

    # 태스크 상세 보기 다이얼로그
    if st.session_state.view_task_id == task['id']:
        show_task_detail_dialog(task)


@st.dialog("태스크 상세", width="large")
def show_task_detail_dialog(task):
    """태스크 상세 정보 다이얼로그"""

    # 편집 모드 체크
    is_editing = st.session_state.get('edit_task_id') == task['id']

    if is_editing:
        # 편집 폼
        show_task_edit_form(task)
    else:
        # 상세 보기 (읽기 전용)
        st.subheader(task['title'])

        # 상태 및 우선순위
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**상태**: {utils.get_status_icon(task['status'])} {task['status']}")
        with col2:
            st.write(f"**우선순위**: {utils.get_priority_badge(task['priority'])}")

        # 설명
        if task.get('description'):
            st.markdown("### 설명")
            st.write(task['description'])

        # 태그
        if task.get('tags'):
            st.markdown("### 태그")
            st.write(utils.get_tag_icon(task['tags']) + " " + task['tags'])

        # 마감일 및 예상 시간
        col1, col2 = st.columns(2)
        with col1:
            if task.get('due_date'):
                st.markdown("### 마감일")
                st.write(utils.format_date(task['due_date']))
                st.caption(utils.get_due_date_badge(task['due_date']))
        with col2:
            if task.get('estimated_hours'):
                st.markdown("### 예상 시간")
                st.write(utils.format_hours(task['estimated_hours']))

        # 체크리스트
        checklist_items = db.get_checklist_items(task['id'])
        if checklist_items:
            st.markdown("### 체크리스트")
            for item in checklist_items:
                checked = st.checkbox(
                    item['content'],
                    value=item['is_checked'],
                    key=f"check_{item['id']}"
                )
                if checked != item['is_checked']:
                    db.update_checklist_item(item['id'], checked)
                    st.rerun()

        # 타임스탬프
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if task.get('created_at'):
                st.caption(f"📅 생성: {utils.format_datetime(task['created_at'])}")
        with col2:
            if task.get('started_at'):
                st.caption(f"▶️ 시작: {utils.format_datetime(task['started_at'])}")
        with col3:
            if task.get('completed_at'):
                st.caption(f"✅ 완료: {utils.format_datetime(task['completed_at'])}")

        # 액션 버튼
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 수정", use_container_width=True, type="primary"):
                st.session_state.edit_task_id = task['id']
                st.rerun()
        with col2:
            if st.button("닫기", use_container_width=True):
                st.session_state.view_task_id = None
                st.rerun()


def show_task_edit_form(task):
    """태스크 수정 폼"""

    st.subheader("✏️ 태스크 수정")

    # 체크리스트 관리 (폼 밖에서 처리)
    st.markdown("### ✅ 체크리스트 관리")
    checklist_items = db.get_checklist_items(task['id'])

    if checklist_items:
        st.caption("기존 항목 (삭제하려면 🗑️ 클릭):")
        for item in checklist_items:
            col_check, col_text, col_delete = st.columns([0.5, 3, 0.5])
            with col_check:
                st.checkbox("", value=item['is_checked'], disabled=True, key=f"edit_check_{item['id']}")
            with col_text:
                st.text(item['content'])
            with col_delete:
                if st.button("🗑️", key=f"del_check_{item['id']}", help="항목 삭제"):
                    db.delete_checklist_item(item['id'])
                    st.rerun()
    else:
        st.info("체크리스트 항목이 없습니다. 아래에서 추가할 수 있습니다.")

    st.markdown("---")

    with st.form("edit_task_form"):
        # 제목
        title = st.text_input("제목*", value=task['title'], max_chars=200)

        # 설명
        description = st.text_area("설명", value=task.get('description') or '', height=100)

        # 상태, 우선순위
        col1, col2 = st.columns(2)
        with col1:
            status_options = ['todo', 'in_progress', 'done']
            status_labels = {'todo': '📝 To Do', 'in_progress': '🔄 In Progress', 'done': '✅ Done'}
            current_status_index = status_options.index(task['status'])
            status = st.selectbox(
                "상태",
                options=status_options,
                format_func=lambda x: status_labels[x],
                index=current_status_index
            )

        with col2:
            priority_options = ['low', 'medium', 'high']
            priority_labels = {'low': '🟢 Low', 'medium': '🟡 Medium', 'high': '🔴 High'}
            current_priority_index = priority_options.index(task['priority'])
            priority = st.selectbox(
                "우선순위",
                options=priority_options,
                format_func=lambda x: priority_labels[x],
                index=current_priority_index
            )

        # 태그
        tags_input = st.text_input("태그 (쉼표로 구분)", value=task.get('tags') or '', placeholder="Dev,Design,Test")

        # 마감일, 예상 시간
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("마감일", value=task.get('due_date'))
        with col2:
            estimated_hours = st.number_input(
                "예상 시간 (시간)",
                min_value=0.0,
                max_value=999.0,
                value=float(task.get('estimated_hours') or 0),
                step=0.5
            )

        # 새 체크리스트 항목 추가
        st.markdown("### ➕ 새 체크리스트 항목 추가")
        new_checklist = st.text_area(
            "한 줄에 하나씩 입력",
            height=100,
            placeholder="예:\nAPI 키 발급\n연동 테스트\n에러 처리",
            key="new_checklist_items"
        )

        # 버튼
        col_cancel, col_submit = st.columns(2)
        with col_cancel:
            cancel = st.form_submit_button("취소", use_container_width=True)
        with col_submit:
            submit = st.form_submit_button("저장", type="primary", use_container_width=True)

        if cancel:
            st.session_state.edit_task_id = None
            st.rerun()

        if submit:
            # 입력 검증
            errors = utils.validate_task_input(title, due_date)

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # 태스크 수정
                success = db.update_task(
                    task['id'],
                    title=title.strip(),
                    description=description.strip() if description else None,
                    status=status,
                    priority=priority,
                    tags=tags_input.strip() if tags_input else None,
                    estimated_hours=estimated_hours if estimated_hours > 0 else None,
                    due_date=due_date
                )

                if success:
                    # 새 체크리스트 항목 추가
                    if new_checklist and new_checklist.strip():
                        items = new_checklist.strip().split('\n')
                        for item_content in items:
                            item_content = item_content.strip()
                            if item_content:  # 빈 줄 무시
                                db.insert_checklist_item(task['id'], item_content)

                    st.success("✅ 태스크가 수정되었습니다!")
                    st.session_state.edit_task_id = None
                    st.rerun()
                else:
                    st.error("태스크 수정에 실패했습니다.")
