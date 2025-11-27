"""
Project Tracker - Configuration Module
Streamlit secrets에서 데이터베이스 설정 읽기
"""

import streamlit as st


def get_db_config():
    """
    Streamlit secrets에서 MySQL 연결 정보 가져오기

    Returns:
        dict: MySQL 연결 설정
        {
            'host': str,
            'port': int,
            'user': str,
            'password': str,
            'database': str
        }
    """
    try:
        db_config = {
            'host': st.secrets["mysql"]["host"],
            'port': st.secrets["mysql"]["port"],
            'user': st.secrets["mysql"]["user"],
            'password': st.secrets["mysql"]["password"],
            'database': st.secrets["mysql"]["database"]
        }
        return db_config
    except Exception as e:
        st.error(f"❌ 설정 파일 읽기 오류: {e}")
        st.info("💡 .streamlit/secrets.toml 파일을 확인해주세요")
        return None


# 앱 설정
APP_TITLE = "📋 Project Tracker"
APP_ICON = "📋"
PAGE_CONFIG = {
    "page_title": "Project Tracker",
    "page_icon": "📋",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 태그 아이콘 매핑
TAG_ICONS = {
    'Dev': '💻',
    'Design': '🎨',
    'Test': '🧪',
    'Deploy': '🚀',
    'Docs': '📝',
    'API': '🔌',
    'Setup': '⚙️',
    'Plan': '📋'
}

# 우선순위 색상
PRIORITY_COLORS = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🔴'
}

# 상태 아이콘
STATUS_ICONS = {
    'todo': '📝',
    'in_progress': '🔄',
    'done': '✅'
}

# 상태 이름 (한글)
STATUS_NAMES = {
    'todo': 'To Do',
    'in_progress': 'In Progress',
    'done': 'Done'
}

# 프로젝트 상태
PROJECT_STATUS = {
    'active': '진행중',
    'completed': '완료',
    'on_hold': '보류'
}
