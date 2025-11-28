"""
Project Tracker - Dashboard View
대시보드 탭 렌더링
"""

import streamlit as st
import plotly.express as px
import db_manager as db
import utils


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
