"""
Project Tracker - Database Manager
MySQL 데이터베이스 CRUD 작업 관리
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import streamlit as st
from config import get_db_config


# ========================================
# 데이터베이스 연결
# ========================================

def get_connection():
    """
    MySQL 데이터베이스 연결 생성

    Returns:
        connection: MySQL 연결 객체 또는 None
    """
    try:
        db_config = get_db_config()
        if not db_config:
            return None

        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        st.error(f"❌ 데이터베이스 연결 실패: {e}")
        return None


def execute_query(query: str, params: tuple = None, fetch: bool = False) -> Optional[Any]:
    """
    SQL 쿼리 실행 (INSERT, UPDATE, DELETE)

    Args:
        query: SQL 쿼리
        params: 쿼리 파라미터
        fetch: True면 결과 반환, False면 lastrowid 반환

    Returns:
        fetch=True: 쿼리 결과 리스트
        fetch=False: lastrowid (INSERT) 또는 rowcount
    """
    connection = get_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    except Error as e:
        st.error(f"❌ 쿼리 실행 오류: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ========================================
# 프로젝트 관련 함수
# ========================================

def insert_project(name: str, description: str = None, github_url: str = None,
                   start_date: date = None, target_end_date: date = None,
                   status: str = 'active', user_id: int = None) -> Optional[int]:
    """
    프로젝트 생성

    Args:
        name: 프로젝트명
        description: 설명
        github_url: GitHub 저장소 URL
        start_date: 시작일
        target_end_date: 목표 완료일
        status: 상태 (active/completed/on_hold)
        user_id: 사용자 ID

    Returns:
        int: 생성된 프로젝트 ID 또는 None
    """
    if not start_date:
        start_date = date.today()

    query = """
        INSERT INTO projects (user_id, name, description, github_url, start_date, target_end_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (user_id, name, description, github_url, start_date, target_end_date, status)
    return execute_query(query, params)


def get_project(project_id: int) -> Optional[Dict]:
    """
    프로젝트 조회

    Args:
        project_id: 프로젝트 ID

    Returns:
        dict: 프로젝트 정보 또는 None
    """
    query = "SELECT * FROM projects WHERE id = %s"
    result = execute_query(query, (project_id,), fetch=True)
    return result[0] if result else None


def get_projects(status: str = None, user_id: int = None) -> List[Dict]:
    """
    프로젝트 목록 조회

    Args:
        status: 필터링할 상태 (None이면 전체)
        user_id: 사용자 ID (None이면 전체, 지정하면 해당 사용자의 프로젝트만)

    Returns:
        list: 프로젝트 리스트
    """
    conditions = []
    params = []

    if user_id is not None:
        conditions.append("user_id = %s")
        params.append(user_id)

    if status:
        conditions.append("status = %s")
        params.append(status)

    if conditions:
        query = f"SELECT * FROM projects WHERE {' AND '.join(conditions)} ORDER BY created_at DESC"
    else:
        query = "SELECT * FROM projects ORDER BY created_at DESC"

    result = execute_query(query, tuple(params) if params else None, fetch=True)
    return result or []


def update_project(project_id: int, **kwargs) -> bool:
    """
    프로젝트 수정

    Args:
        project_id: 프로젝트 ID
        **kwargs: 수정할 필드들 (name, description, github_url, start_date, target_end_date, status)

    Returns:
        bool: 성공 여부
    """
    fields = []
    values = []

    for key, value in kwargs.items():
        if key in ['name', 'description', 'github_url', 'start_date', 'target_end_date', 'status']:
            fields.append(f"{key} = %s")
            values.append(value)

    if not fields:
        return False

    query = f"UPDATE projects SET {', '.join(fields)} WHERE id = %s"
    values.append(project_id)

    result = execute_query(query, tuple(values))
    return result is not None and result > 0


def delete_project(project_id: int) -> bool:
    """
    프로젝트 삭제 (CASCADE로 연관 데이터도 삭제됨)

    Args:
        project_id: 프로젝트 ID

    Returns:
        bool: 성공 여부
    """
    query = "DELETE FROM projects WHERE id = %s"
    result = execute_query(query, (project_id,))
    return result is not None and result > 0


# ========================================
# 태스크 관련 함수
# ========================================

def insert_task(project_id: int, title: str, description: str = None,
                status: str = 'todo', priority: str = 'medium',
                tags: str = None, estimated_hours: float = None,
                due_date: date = None) -> Optional[int]:
    """
    태스크 생성

    Args:
        project_id: 프로젝트 ID
        title: 태스크 제목
        description: 설명
        status: 상태 (todo/in_progress/done)
        priority: 우선순위 (low/medium/high)
        tags: 태그 (쉼표 구분)
        estimated_hours: 예상 시간
        due_date: 마감일

    Returns:
        int: 생성된 태스크 ID 또는 None
    """
    query = """
        INSERT INTO tasks (project_id, title, description, status, priority,
                          tags, estimated_hours, due_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (project_id, title, description, status, priority,
              tags, estimated_hours, due_date)
    return execute_query(query, params)


def get_task(task_id: int) -> Optional[Dict]:
    """
    태스크 조회

    Args:
        task_id: 태스크 ID

    Returns:
        dict: 태스크 정보 또는 None
    """
    query = "SELECT * FROM tasks WHERE id = %s"
    result = execute_query(query, (task_id,), fetch=True)
    return result[0] if result else None


def get_tasks(project_id: int, status: str = None) -> List[Dict]:
    """
    프로젝트의 태스크 목록 조회

    Args:
        project_id: 프로젝트 ID
        status: 필터링할 상태 (None이면 전체)

    Returns:
        list: 태스크 리스트
    """
    if status:
        query = """
            SELECT * FROM tasks
            WHERE project_id = %s AND status = %s
            ORDER BY created_at DESC
        """
        params = (project_id, status)
    else:
        query = """
            SELECT * FROM tasks
            WHERE project_id = %s
            ORDER BY created_at DESC
        """
        params = (project_id,)

    result = execute_query(query, params, fetch=True)
    return result or []


def update_task(task_id: int, **kwargs) -> bool:
    """
    태스크 수정

    Args:
        task_id: 태스크 ID
        **kwargs: 수정할 필드들

    Returns:
        bool: 성공 여부
    """
    valid_fields = ['title', 'description', 'status', 'priority', 'tags',
                    'estimated_hours', 'due_date', 'started_at', 'completed_at']

    fields = []
    values = []

    for key, value in kwargs.items():
        if key in valid_fields:
            fields.append(f"{key} = %s")
            values.append(value)

    if not fields:
        return False

    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s"
    values.append(task_id)

    result = execute_query(query, tuple(values))
    return result is not None and result > 0


def update_task_status(task_id: int, new_status: str) -> bool:
    """
    태스크 상태 변경 (시간 자동 기록)

    Args:
        task_id: 태스크 ID
        new_status: 새 상태 (todo/in_progress/done)

    Returns:
        bool: 성공 여부
    """
    updates = {'status': new_status}

    if new_status == 'in_progress':
        updates['started_at'] = datetime.now()
    elif new_status == 'done':
        updates['completed_at'] = datetime.now()

    return update_task(task_id, **updates)


def delete_task(task_id: int) -> bool:
    """
    태스크 삭제

    Args:
        task_id: 태스크 ID

    Returns:
        bool: 성공 여부
    """
    query = "DELETE FROM tasks WHERE id = %s"
    result = execute_query(query, (task_id,))
    return result is not None and result > 0


def count_tasks(project_id: int, status: str = None) -> int:
    """
    태스크 개수 세기

    Args:
        project_id: 프로젝트 ID
        status: 필터링할 상태 (None이면 전체)

    Returns:
        int: 태스크 개수
    """
    if status:
        query = "SELECT COUNT(*) as count FROM tasks WHERE project_id = %s AND status = %s"
        params = (project_id, status)
    else:
        query = "SELECT COUNT(*) as count FROM tasks WHERE project_id = %s"
        params = (project_id,)

    result = execute_query(query, params, fetch=True)
    return result[0]['count'] if result else 0


# ========================================
# 체크리스트 관련 함수
# ========================================

def insert_checklist_item(task_id: int, content: str, is_checked: bool = False) -> Optional[int]:
    """
    체크리스트 항목 추가

    Args:
        task_id: 태스크 ID
        content: 항목 내용
        is_checked: 체크 여부

    Returns:
        int: 생성된 항목 ID 또는 None
    """
    query = """
        INSERT INTO checklist_items (task_id, content, is_checked)
        VALUES (%s, %s, %s)
    """
    params = (task_id, content, is_checked)
    return execute_query(query, params)


def get_checklist_items(task_id: int) -> List[Dict]:
    """
    태스크의 체크리스트 항목 조회

    Args:
        task_id: 태스크 ID

    Returns:
        list: 체크리스트 항목 리스트
    """
    query = "SELECT * FROM checklist_items WHERE task_id = %s ORDER BY created_at"
    result = execute_query(query, (task_id,), fetch=True)
    return result or []


def update_checklist_item(item_id: int, is_checked: bool) -> bool:
    """
    체크리스트 항목 체크 상태 변경

    Args:
        item_id: 항목 ID
        is_checked: 체크 여부

    Returns:
        bool: 성공 여부
    """
    query = "UPDATE checklist_items SET is_checked = %s WHERE id = %s"
    result = execute_query(query, (is_checked, item_id))
    return result is not None and result > 0


def delete_checklist_item(item_id: int) -> bool:
    """
    체크리스트 항목 삭제

    Args:
        item_id: 항목 ID

    Returns:
        bool: 성공 여부
    """
    query = "DELETE FROM checklist_items WHERE id = %s"
    result = execute_query(query, (item_id,))
    return result is not None and result > 0


# ========================================
# 마일스톤 관련 함수
# ========================================

def insert_milestone(project_id: int, title: str, description: str = None,
                     target_date: date = None) -> Optional[int]:
    """
    마일스톤 생성

    Args:
        project_id: 프로젝트 ID
        title: 마일스톤명
        description: 설명
        target_date: 목표 날짜

    Returns:
        int: 생성된 마일스톤 ID 또는 None
    """
    query = """
        INSERT INTO milestones (project_id, title, description, target_date)
        VALUES (%s, %s, %s, %s)
    """
    params = (project_id, title, description, target_date)
    return execute_query(query, params)


def get_milestones(project_id: int) -> List[Dict]:
    """
    프로젝트의 마일스톤 목록 조회

    Args:
        project_id: 프로젝트 ID

    Returns:
        list: 마일스톤 리스트
    """
    query = """
        SELECT * FROM milestones
        WHERE project_id = %s
        ORDER BY target_date
    """
    result = execute_query(query, (project_id,), fetch=True)
    return result or []


def update_milestone_status(milestone_id: int, is_completed: bool) -> bool:
    """
    마일스톤 완료 상태 변경

    Args:
        milestone_id: 마일스톤 ID
        is_completed: 완료 여부

    Returns:
        bool: 성공 여부
    """
    completed_at = datetime.now() if is_completed else None

    query = """
        UPDATE milestones
        SET is_completed = %s, completed_at = %s
        WHERE id = %s
    """
    params = (is_completed, completed_at, milestone_id)
    result = execute_query(query, params)
    return result is not None and result > 0


def delete_milestone(milestone_id: int) -> bool:
    """
    마일스톤 삭제

    Args:
        milestone_id: 마일스톤 ID

    Returns:
        bool: 성공 여부
    """
    query = "DELETE FROM milestones WHERE id = %s"
    result = execute_query(query, (milestone_id,))
    return result is not None and result > 0


# ========================================
# 회고 관련 함수
# ========================================

def insert_retrospective(project_id: int, keep_content: str = None,
                        problem_content: str = None, try_content: str = None,
                        learning_content: str = None) -> Optional[int]:
    """
    회고 생성

    Args:
        project_id: 프로젝트 ID
        keep_content: Keep - 계속할 것
        problem_content: Problem - 문제점
        try_content: Try - 시도할 것
        learning_content: 학습 내용

    Returns:
        int: 생성된 회고 ID 또는 None
    """
    query = """
        INSERT INTO retrospectives
        (project_id, keep_content, problem_content, try_content, learning_content)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (project_id, keep_content, problem_content, try_content, learning_content)
    return execute_query(query, params)


def get_retrospective(project_id: int) -> Optional[Dict]:
    """
    프로젝트의 회고 조회

    Args:
        project_id: 프로젝트 ID

    Returns:
        dict: 회고 정보 또는 None
    """
    query = "SELECT * FROM retrospectives WHERE project_id = %s"
    result = execute_query(query, (project_id,), fetch=True)
    return result[0] if result else None


def update_retrospective(project_id: int, keep_content: str = None,
                        problem_content: str = None, try_content: str = None,
                        learning_content: str = None) -> bool:
    """
    회고 수정

    Args:
        project_id: 프로젝트 ID
        keep_content: Keep - 계속할 것
        problem_content: Problem - 문제점
        try_content: Try - 시도할 것
        learning_content: 학습 내용

    Returns:
        bool: 성공 여부
    """
    query = """
        UPDATE retrospectives
        SET keep_content = %s, problem_content = %s,
            try_content = %s, learning_content = %s
        WHERE project_id = %s
    """
    params = (keep_content, problem_content, try_content, learning_content, project_id)
    result = execute_query(query, params)
    return result is not None and result > 0


def get_all_retrospectives() -> List[Dict]:
    """
    모든 회고 조회 (프로젝트 정보 포함)

    Returns:
        list: 회고 리스트
    """
    query = """
        SELECT r.*, p.name as project_name
        FROM retrospectives r
        JOIN projects p ON r.project_id = p.id
        ORDER BY r.created_at DESC
    """
    result = execute_query(query, fetch=True)
    return result or []


# ========================================
# 사용자 인증 관련 함수
# ========================================

import hashlib


def hash_password(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해시된 비밀번호
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email: str, password: str, username: str) -> Optional[int]:
    """
    사용자 생성 (회원가입)

    Args:
        email: 이메일
        password: 비밀번호 (평문)
        username: 사용자 이름

    Returns:
        int: 생성된 사용자 ID 또는 None
    """
    password_hash = hash_password(password)

    query = """
        INSERT INTO users (email, password_hash, username)
        VALUES (%s, %s, %s)
    """
    params = (email, password_hash, username)
    return execute_query(query, params)


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    이메일로 사용자 조회

    Args:
        email: 이메일

    Returns:
        dict: 사용자 정보 또는 None
    """
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_query(query, (email,), fetch=True)
    return result[0] if result else None


def verify_user(email: str, password: str) -> Optional[Dict]:
    """
    사용자 인증 (로그인)

    Args:
        email: 이메일
        password: 비밀번호 (평문)

    Returns:
        dict: 인증 성공 시 사용자 정보, 실패 시 None
    """
    user = get_user_by_email(email)

    if not user:
        return None

    password_hash = hash_password(password)

    if user['password_hash'] == password_hash:
        # 마지막 로그인 시간 업데이트
        update_last_login(user['id'])
        return user

    return None


def update_last_login(user_id: int) -> bool:
    """
    마지막 로그인 시간 업데이트

    Args:
        user_id: 사용자 ID

    Returns:
        bool: 성공 여부
    """
    query = "UPDATE users SET last_login = NOW() WHERE id = %s"
    result = execute_query(query, (user_id,))
    return result is not None and result > 0
