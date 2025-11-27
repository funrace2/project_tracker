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

if 'view_task_id' not in st.session_state:
    st.session_state.view_task_id = None

if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None


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

    project_id = project['id']

    # 태스크 데이터 가져오기
    all_tasks = db.get_tasks(project_id)
    metrics = utils.calculate_project_metrics(all_tasks)

    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 전체 태스크", metrics['total'])

    with col2:
        st.metric("✅ 완료", metrics['done'])

    with col3:
        st.metric("📊 진행률", f"{metrics['progress_rate']:.0f}%")

    with col4:
        if project.get('target_end_date'):
            days_left = utils.days_until(project['target_end_date'])
            if days_left >= 0:
                st.metric("⏰ 남은 기간", f"{days_left}일")
            else:
                st.metric("⏰ 기간", f"D+{abs(days_left)}")
        else:
            st.metric("⏰ 남은 기간", "미설정")

    st.markdown("---")

    # 차트 영역
    if not all_tasks:
        st.info("📊 태스크가 없어서 차트를 표시할 수 없습니다. Kanban 보드에서 태스크를 추가해보세요!")
        return

    # 2개 컬럼으로 차트 배치
    col1, col2 = st.columns(2)

    with col1:
        # 상태별 분포 (원형 차트)
        st.markdown("### 📊 상태별 태스크 분포")
        status_dist = utils.get_status_distribution(all_tasks)

        fig_pie = px.pie(
            names=['📝 To Do', '🔄 In Progress', '✅ Done'],
            values=[status_dist['todo'], status_dist['in_progress'], status_dist['done']],
            color_discrete_sequence=['#FFA07A', '#87CEEB', '#90EE90']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # 우선순위별 분포 (막대 차트)
        st.markdown("### 🎯 우선순위별 분포")
        priority_dist = utils.get_priority_distribution(all_tasks)

        fig_bar = px.bar(
            x=['🟢 Low', '🟡 Medium', '🔴 High'],
            y=[priority_dist['low'], priority_dist['medium'], priority_dist['high']],
            labels={'x': '우선순위', 'y': '개수'},
            color=['🟢 Low', '🟡 Medium', '🔴 High'],
            color_discrete_sequence=['#90EE90', '#FFD700', '#FF6B6B']
        )
        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="태스크 개수")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 진행률 추이 (완료된 태스크가 있을 때만)
    done_tasks = [t for t in all_tasks if t['status'] == 'done' and t.get('completed_at')]
    if done_tasks:
        st.markdown("### 📈 진행률 추이")
        df_progress = utils.prepare_progress_history(all_tasks)

        if not df_progress.empty:
            fig_line = px.line(
                df_progress,
                x='date',
                y='progress_rate',
                labels={'date': '날짜', 'progress_rate': '완료율 (%)'},
                markers=True
            )
            fig_line.update_layout(
                yaxis_range=[0, 100],
                showlegend=False,
                hovermode='x unified'
            )

            # 목표선 추가 (100%)
            fig_line.add_hline(
                y=100,
                line_dash="dash",
                line_color="green",
                annotation_text="목표 (100%)"
            )

            st.plotly_chart(fig_line, use_container_width=True)

    # 태그별 분포
    tag_dist = utils.get_tag_distribution(all_tasks)
    if tag_dist:
        st.markdown("### 🏷️ 태그별 분포")
        col1, col2 = st.columns([2, 1])

        with col1:
            fig_tag = px.bar(
                x=list(tag_dist.keys()),
                y=list(tag_dist.values()),
                labels={'x': '태그', 'y': '개수'},
                color=list(tag_dist.keys()),
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_tag.update_layout(showlegend=False, xaxis_title="", yaxis_title="태스크 개수")
            st.plotly_chart(fig_tag, use_container_width=True)

        with col2:
            st.markdown("#### 태그 목록")
            for tag, count in tag_dist.items():
                icon = utils.get_tag_icon(tag)
                st.write(f"{icon} **{tag}**: {count}개")

    st.markdown("---")

    # 마일스톤 섹션
    st.markdown("### 📅 마일스톤")

    milestones = db.get_milestones(project_id)

    if not milestones:
        st.info("📅 마일스톤이 없습니다.")

        # 마일스톤 추가 폼
        with st.expander("➕ 마일스톤 추가"):
            with st.form("add_milestone_form"):
                title = st.text_input("마일스톤명*", placeholder="예: MVP 완성")
                description = st.text_area("설명", placeholder="상세 설명 (선택)")
                target_date = st.date_input("목표 날짜*")

                submitted = st.form_submit_button("추가", type="primary")

                if submitted:
                    if not title:
                        st.error("마일스톤명은 필수입니다.")
                    elif not target_date:
                        st.error("목표 날짜는 필수입니다.")
                    else:
                        milestone_id = db.insert_milestone(
                            project_id=project_id,
                            title=title.strip(),
                            description=description.strip() if description else None,
                            target_date=target_date
                        )
                        if milestone_id:
                            st.success("✅ 마일스톤이 추가되었습니다!")
                            st.rerun()
    else:
        # 마일스톤 목록 표시
        for milestone in milestones:
            col1, col2, col3 = st.columns([0.5, 3, 0.5])

            with col1:
                # 완료 체크박스
                is_completed = st.checkbox(
                    "",
                    value=milestone['is_completed'],
                    key=f"milestone_{milestone['id']}",
                    label_visibility="collapsed"
                )
                if is_completed != milestone['is_completed']:
                    db.update_milestone_status(milestone['id'], is_completed)
                    st.rerun()

            with col2:
                # 마일스톤 정보
                status_icon = "✅" if milestone['is_completed'] else "⏳"
                st.markdown(f"{status_icon} **{milestone['title']}**")

                # 날짜 및 설명
                date_text = utils.format_date(milestone['target_date'])
                days_to = utils.days_until(milestone['target_date'])

                if milestone['is_completed']:
                    st.caption(f"📅 {date_text} (완료)")
                elif days_to < 0:
                    st.caption(f"📅 {date_text} (🔴 {abs(days_to)}일 지남)")
                elif days_to == 0:
                    st.caption(f"📅 {date_text} (🔥 D-Day)")
                elif days_to <= 3:
                    st.caption(f"📅 {date_text} (🟡 D-{days_to})")
                else:
                    st.caption(f"📅 {date_text} (🟢 D-{days_to})")

                if milestone.get('description'):
                    st.caption(milestone['description'])

            with col3:
                # 삭제 버튼
                if st.button("🗑️", key=f"del_milestone_{milestone['id']}", help="삭제"):
                    db.delete_milestone(milestone['id'])
                    st.rerun()

        # 마일스톤 추가 폼
        with st.expander("➕ 마일스톤 추가"):
            with st.form("add_milestone_form"):
                title = st.text_input("마일스톤명*", placeholder="예: MVP 완성")
                description = st.text_area("설명", placeholder="상세 설명 (선택)")
                target_date = st.date_input("목표 날짜*")

                submitted = st.form_submit_button("추가", type="primary")

                if submitted:
                    if not title:
                        st.error("마일스톤명은 필수입니다.")
                    elif not target_date:
                        st.error("목표 날짜는 필수입니다.")
                    else:
                        milestone_id = db.insert_milestone(
                            project_id=project_id,
                            title=title.strip(),
                            description=description.strip() if description else None,
                            target_date=target_date
                        )
                        if milestone_id:
                            st.success("✅ 마일스톤이 추가되었습니다!")
                            st.rerun()


# ========================================
# Kanban 보드 탭
# ========================================

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
