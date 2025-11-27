"""
Project Tracker - Utility Functions
유틸리티 함수 모음
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import pandas as pd
from config import TAG_ICONS, PRIORITY_COLORS, STATUS_ICONS


# ========================================
# 진행률 계산
# ========================================

def calculate_progress_rate(total: int, completed: int) -> float:
    """
    진행률 계산

    Args:
        total: 전체 개수
        completed: 완료 개수

    Returns:
        float: 진행률 (0-100)
    """
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 1)


def calculate_project_metrics(tasks: List[Dict]) -> Dict:
    """
    프로젝트 메트릭 계산

    Args:
        tasks: 태스크 리스트

    Returns:
        dict: 메트릭 정보
        {
            'total': int,
            'todo': int,
            'in_progress': int,
            'done': int,
            'progress_rate': float
        }
    """
    total = len(tasks)
    todo = len([t for t in tasks if t['status'] == 'todo'])
    in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
    done = len([t for t in tasks if t['status'] == 'done'])

    return {
        'total': total,
        'todo': todo,
        'in_progress': in_progress,
        'done': done,
        'progress_rate': calculate_progress_rate(total, done)
    }


# ========================================
# 날짜 관련 함수
# ========================================

def days_until(target_date: date) -> int:
    """
    오늘부터 목표 날짜까지 남은 일수

    Args:
        target_date: 목표 날짜

    Returns:
        int: 남은 일수 (음수면 지난 날)
    """
    if not target_date:
        return 0
    delta = target_date - date.today()
    return delta.days


def format_date(dt: date) -> str:
    """
    날짜를 한글 형식으로 포맷팅

    Args:
        dt: 날짜

    Returns:
        str: 포맷된 날짜 (예: "2024년 11월 23일")
    """
    if not dt:
        return ""
    return dt.strftime("%Y년 %m월 %d일")


def format_datetime(dt: datetime) -> str:
    """
    날짜시간을 한글 형식으로 포맷팅

    Args:
        dt: 날짜시간

    Returns:
        str: 포맷된 날짜시간 (예: "2024년 11월 23일 15:30")
    """
    if not dt:
        return ""
    return dt.strftime("%Y년 %m월 %d일 %H:%M")


def get_date_range_text(start_date: date, end_date: date = None) -> str:
    """
    날짜 범위를 텍스트로 변환

    Args:
        start_date: 시작일
        end_date: 종료일

    Returns:
        str: 날짜 범위 텍스트
    """
    if not start_date:
        return ""

    text = format_date(start_date)
    if end_date:
        text += f" ~ {format_date(end_date)}"

    return text


def get_relative_time(dt: datetime) -> str:
    """
    상대적 시간 표시 (예: "2시간 전", "3일 전")

    Args:
        dt: 날짜시간

    Returns:
        str: 상대적 시간 텍스트
    """
    if not dt:
        return ""

    now = datetime.now()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"


# ========================================
# 태스크 관련 유틸리티
# ========================================

def get_tag_icon(tags: str) -> str:
    """
    태그 문자열을 아이콘으로 변환

    Args:
        tags: 태그 문자열 (쉼표 구분)

    Returns:
        str: 태그 아이콘들
    """
    if not tags:
        return ""

    tag_list = [tag.strip() for tag in tags.split(',')]
    icons = [TAG_ICONS.get(tag, tag) for tag in tag_list]
    return ' '.join(icons)


def get_priority_badge(priority: str) -> str:
    """
    우선순위 배지 (색상 + 텍스트)

    Args:
        priority: 우선순위 (low/medium/high)

    Returns:
        str: 우선순위 배지
    """
    color = PRIORITY_COLORS.get(priority, '⚪')
    text_map = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High'
    }
    text = text_map.get(priority, priority)
    return f"{color} {text}"


def get_status_icon(status: str) -> str:
    """
    상태 아이콘 가져오기

    Args:
        status: 상태 (todo/in_progress/done)

    Returns:
        str: 상태 아이콘
    """
    return STATUS_ICONS.get(status, '❓')


def get_due_date_badge(due_date: date) -> str:
    """
    마감일 배지 (D-day 표시)

    Args:
        due_date: 마감일

    Returns:
        str: 마감일 배지
    """
    if not due_date:
        return ""

    days = days_until(due_date)

    if days < 0:
        return f"🔴 D+{abs(days)} (지남)"
    elif days == 0:
        return "🔥 D-Day"
    elif days <= 3:
        return f"🟡 D-{days}"
    else:
        return f"🟢 D-{days}"


# ========================================
# 데이터 변환
# ========================================

def tasks_to_dataframe(tasks: List[Dict]) -> pd.DataFrame:
    """
    태스크 리스트를 DataFrame으로 변환

    Args:
        tasks: 태스크 리스트

    Returns:
        DataFrame: 태스크 데이터프레임
    """
    if not tasks:
        return pd.DataFrame()

    return pd.DataFrame(tasks)


def get_tag_distribution(tasks: List[Dict]) -> Dict[str, int]:
    """
    태그별 태스크 분포 계산

    Args:
        tasks: 태스크 리스트

    Returns:
        dict: 태그별 개수
    """
    tag_count = {}

    for task in tasks:
        if task.get('tags'):
            tags = [tag.strip() for tag in task['tags'].split(',')]
            for tag in tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1

    return tag_count


def get_priority_distribution(tasks: List[Dict]) -> Dict[str, int]:
    """
    우선순위별 태스크 분포 계산

    Args:
        tasks: 태스크 리스트

    Returns:
        dict: 우선순위별 개수
    """
    priority_count = {'low': 0, 'medium': 0, 'high': 0}

    for task in tasks:
        priority = task.get('priority', 'medium')
        if priority in priority_count:
            priority_count[priority] += 1

    return priority_count


def get_status_distribution(tasks: List[Dict]) -> Dict[str, int]:
    """
    상태별 태스크 분포 계산

    Args:
        tasks: 태스크 리스트

    Returns:
        dict: 상태별 개수
    """
    status_count = {'todo': 0, 'in_progress': 0, 'done': 0}

    for task in tasks:
        status = task.get('status', 'todo')
        if status in status_count:
            status_count[status] += 1

    return status_count


# ========================================
# 차트 데이터 준비
# ========================================

def prepare_progress_history(tasks: List[Dict]) -> pd.DataFrame:
    """
    진행률 추이 데이터 준비 (날짜별 완료 개수)

    Args:
        tasks: 태스크 리스트

    Returns:
        DataFrame: 날짜별 진행률 데이터
    """
    completed_tasks = [t for t in tasks if t['status'] == 'done' and t.get('completed_at')]

    if not completed_tasks:
        return pd.DataFrame(columns=['date', 'count', 'cumulative', 'progress_rate'])

    # 완료 날짜별로 그룹화
    completion_dates = {}
    for task in completed_tasks:
        completed_at = task['completed_at']
        if isinstance(completed_at, datetime):
            date_key = completed_at.date()
        else:
            date_key = completed_at

        completion_dates[date_key] = completion_dates.get(date_key, 0) + 1

    # 날짜 순으로 정렬
    sorted_dates = sorted(completion_dates.items())

    # 누적 합계 계산
    total_tasks = len(tasks)
    cumulative = 0
    data = []

    for date_key, count in sorted_dates:
        cumulative += count
        progress_rate = (cumulative / total_tasks * 100) if total_tasks > 0 else 0

        data.append({
            'date': date_key,
            'count': count,
            'cumulative': cumulative,
            'progress_rate': round(progress_rate, 1)
        })

    return pd.DataFrame(data)


# ========================================
# 검증 함수
# ========================================

def validate_project_input(name: str, start_date: date = None,
                          target_end_date: date = None) -> List[str]:
    """
    프로젝트 입력 검증

    Args:
        name: 프로젝트명
        start_date: 시작일
        target_end_date: 목표 완료일

    Returns:
        list: 에러 메시지 리스트 (비어있으면 검증 통과)
    """
    errors = []

    if not name or not name.strip():
        errors.append("프로젝트명은 필수입니다")
    elif len(name) > 200:
        errors.append("프로젝트명은 200자 이내여야 합니다")

    if start_date and target_end_date and start_date > target_end_date:
        errors.append("시작일은 목표일보다 이전이어야 합니다")

    return errors


def validate_task_input(title: str, due_date: date = None) -> List[str]:
    """
    태스크 입력 검증

    Args:
        title: 태스크 제목
        due_date: 마감일

    Returns:
        list: 에러 메시지 리스트 (비어있으면 검증 통과)
    """
    errors = []

    if not title or not title.strip():
        errors.append("태스크 제목은 필수입니다")
    elif len(title) > 200:
        errors.append("태스크 제목은 200자 이내여야 합니다")

    return errors


# ========================================
# 포맷팅 함수
# ========================================

def format_hours(hours: float) -> str:
    """
    시간을 읽기 쉬운 형식으로 변환

    Args:
        hours: 시간 (숫자)

    Returns:
        str: 포맷된 시간 (예: "2시간", "1.5시간")
    """
    if not hours:
        return "미정"

    if hours == int(hours):
        return f"{int(hours)}시간"
    else:
        return f"{hours}시간"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    긴 텍스트를 자르고 ... 추가

    Args:
        text: 원본 텍스트
        max_length: 최대 길이

    Returns:
        str: 잘린 텍스트
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."
