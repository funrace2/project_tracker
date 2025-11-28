"""
Project Tracker - Retrospective View
회고(KPT) 탭 렌더링
"""

import streamlit as st
import db_manager as db
import utils


def render_retrospective_tab(project):
    """회고 탭 렌더링"""

    project_id = project['id']

    st.subheader("📝 프로젝트 회고 (KPT)")
    st.caption("Keep(계속할 것), Problem(문제점), Try(시도할 것)")

    # 기존 회고 데이터 가져오기
    retrospective = db.get_retrospective(project_id)

    # 편집 모드 상태 초기화
    if 'edit_retrospective' not in st.session_state:
        st.session_state.edit_retrospective = False

    st.markdown("---")

    # 회고가 없는 경우 - 작성 폼
    if not retrospective:
        st.info("📝 아직 작성된 회고가 없습니다. 프로젝트를 진행하면서 배운 점을 기록해보세요!")

        with st.form("create_retrospective_form"):
            st.markdown("### 🟢 Keep (계속할 것)")
            st.caption("잘했던 점, 앞으로도 계속 유지하고 싶은 것")
            keep_content = st.text_area(
                "Keep",
                height=150,
                placeholder="예:\n- 매일 아침 스탠드업 미팅\n- 코드 리뷰 문화\n- 페어 프로그래밍",
                label_visibility="collapsed"
            )

            st.markdown("### 🔴 Problem (문제점)")
            st.caption("어려웠던 점, 개선이 필요한 부분")
            problem_content = st.text_area(
                "Problem",
                height=150,
                placeholder="예:\n- 일정 관리의 어려움\n- 기술 스택 선택의 고민\n- 팀 커뮤니케이션 부족",
                label_visibility="collapsed"
            )

            st.markdown("### 🟡 Try (시도할 것)")
            st.caption("다음에 시도해볼 것, 개선 방안")
            try_content = st.text_area(
                "Try",
                height=150,
                placeholder="예:\n- 스프린트 계획 세우기\n- 더 자주 배포하기\n- 문서화 습관 들이기",
                label_visibility="collapsed"
            )

            st.markdown("### 📚 Learning (배운 점)")
            st.caption("프로젝트를 통해 배운 기술이나 인사이트")
            learning_content = st.text_area(
                "Learning",
                height=150,
                placeholder="예:\n- React Hooks 사용법\n- REST API 설계 원칙\n- Git 브랜치 전략",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button("💾 회고 저장", type="primary", use_container_width=True)

            if submitted:
                retrospective_id = db.insert_retrospective(
                    project_id=project_id,
                    keep_content=keep_content.strip() if keep_content else None,
                    problem_content=problem_content.strip() if problem_content else None,
                    try_content=try_content.strip() if try_content else None,
                    learning_content=learning_content.strip() if learning_content else None
                )

                if retrospective_id:
                    st.success("✅ 회고가 저장되었습니다!")
                    st.rerun()
                else:
                    st.error("회고 저장에 실패했습니다.")

    # 회고가 있는 경우 - 읽기 또는 수정 모드
    else:
        # 수정/읽기 모드 토글 버튼
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.session_state.edit_retrospective:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.edit_retrospective = False
                    st.rerun()
            else:
                if st.button("✏️ 수정", use_container_width=True, type="primary"):
                    st.session_state.edit_retrospective = True
                    st.rerun()

        # 읽기 모드
        if not st.session_state.edit_retrospective:
            # Keep
            st.markdown("### 🟢 Keep (계속할 것)")
            if retrospective.get('keep_content'):
                st.markdown(retrospective['keep_content'])
            else:
                st.caption("_작성된 내용이 없습니다._")

            st.markdown("---")

            # Problem
            st.markdown("### 🔴 Problem (문제점)")
            if retrospective.get('problem_content'):
                st.markdown(retrospective['problem_content'])
            else:
                st.caption("_작성된 내용이 없습니다._")

            st.markdown("---")

            # Try
            st.markdown("### 🟡 Try (시도할 것)")
            if retrospective.get('try_content'):
                st.markdown(retrospective['try_content'])
            else:
                st.caption("_작성된 내용이 없습니다._")

            st.markdown("---")

            # Learning
            st.markdown("### 📚 Learning (배운 점)")
            if retrospective.get('learning_content'):
                st.markdown(retrospective['learning_content'])
            else:
                st.caption("_작성된 내용이 없습니다._")

            st.markdown("---")

            # 작성 시간
            if retrospective.get('created_at'):
                st.caption(f"📅 작성일: {utils.format_datetime(retrospective['created_at'])}")
            if retrospective.get('updated_at') and retrospective.get('updated_at') != retrospective.get('created_at'):
                st.caption(f"🔄 수정일: {utils.format_datetime(retrospective['updated_at'])}")

        # 수정 모드
        else:
            with st.form("edit_retrospective_form"):
                st.markdown("### 🟢 Keep (계속할 것)")
                keep_content = st.text_area(
                    "Keep",
                    value=retrospective.get('keep_content') or '',
                    height=150,
                    label_visibility="collapsed"
                )

                st.markdown("### 🔴 Problem (문제점)")
                problem_content = st.text_area(
                    "Problem",
                    value=retrospective.get('problem_content') or '',
                    height=150,
                    label_visibility="collapsed"
                )

                st.markdown("### 🟡 Try (시도할 것)")
                try_content = st.text_area(
                    "Try",
                    value=retrospective.get('try_content') or '',
                    height=150,
                    label_visibility="collapsed"
                )

                st.markdown("### 📚 Learning (배운 점)")
                learning_content = st.text_area(
                    "Learning",
                    value=retrospective.get('learning_content') or '',
                    height=150,
                    label_visibility="collapsed"
                )

                col_cancel, col_submit = st.columns(2)

                with col_cancel:
                    cancel = st.form_submit_button("취소", use_container_width=True)
                with col_submit:
                    submit = st.form_submit_button("💾 저장", type="primary", use_container_width=True)

                if cancel:
                    st.session_state.edit_retrospective = False
                    st.rerun()

                if submit:
                    success = db.update_retrospective(
                        project_id=project_id,
                        keep_content=keep_content.strip() if keep_content else None,
                        problem_content=problem_content.strip() if problem_content else None,
                        try_content=try_content.strip() if try_content else None,
                        learning_content=learning_content.strip() if learning_content else None
                    )

                    if success:
                        st.success("✅ 회고가 수정되었습니다!")
                        st.session_state.edit_retrospective = False
                        st.rerun()
                    else:
                        st.error("회고 수정에 실패했습니다.")
