-- ========================================
-- Project Tracker - Database Schema
-- ========================================
-- DBMS: MySQL 8.0+
-- Charset: utf8mb4
-- Created: 2024-11-23
-- ========================================

-- 데이터베이스 생성 (이미 생성되어 있다면 스킵)
CREATE DATABASE IF NOT EXISTS project_tracker
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE project_tracker;

-- ========================================
-- 1. projects (프로젝트)
-- ========================================
CREATE TABLE IF NOT EXISTS projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '프로젝트명',
    description TEXT COMMENT '프로젝트 설명',
    github_url VARCHAR(500) COMMENT 'GitHub 저장소 URL',
    start_date DATE NOT NULL COMMENT '시작일',
    target_end_date DATE COMMENT '목표 완료일',
    status ENUM('active', 'completed', 'on_hold') DEFAULT 'active' COMMENT '상태',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',

    INDEX idx_status (status),
    INDEX idx_dates (start_date, target_end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='프로젝트';

-- ========================================
-- 2. tasks (태스크)
-- ========================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '프로젝트 ID (FK)',
    title VARCHAR(200) NOT NULL COMMENT '태스크 제목',
    description TEXT COMMENT '상세 설명',
    status ENUM('todo', 'in_progress', 'done') DEFAULT 'todo' COMMENT '상태',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium' COMMENT '우선순위',
    tags VARCHAR(200) COMMENT '태그 (쉼표 구분)',
    estimated_hours DECIMAL(5,2) COMMENT '예상 소요 시간 (시간)',
    due_date DATE COMMENT '마감일',
    started_at TIMESTAMP NULL COMMENT '시작 시간',
    completed_at TIMESTAMP NULL COMMENT '완료 시간',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_due_date (due_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='태스크';

-- ========================================
-- 3. checklist_items (체크리스트 항목)
-- ========================================
CREATE TABLE IF NOT EXISTS checklist_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '태스크 ID (FK)',
    content VARCHAR(300) NOT NULL COMMENT '항목 내용',
    is_checked BOOLEAN DEFAULT FALSE COMMENT '체크 여부',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',

    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    INDEX idx_task (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='체크리스트';

-- ========================================
-- 4. milestones (마일스톤)
-- ========================================
CREATE TABLE IF NOT EXISTS milestones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '프로젝트 ID (FK)',
    title VARCHAR(200) NOT NULL COMMENT '마일스톤명',
    description TEXT COMMENT '설명',
    target_date DATE NOT NULL COMMENT '목표 날짜',
    is_completed BOOLEAN DEFAULT FALSE COMMENT '완료 여부',
    completed_at TIMESTAMP NULL COMMENT '완료 시간',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_target_date (target_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='마일스톤';

-- ========================================
-- 5. retrospectives (회고)
-- ========================================
CREATE TABLE IF NOT EXISTS retrospectives (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '프로젝트 ID (FK)',
    keep_content TEXT COMMENT 'Keep - 계속할 것',
    problem_content TEXT COMMENT 'Problem - 문제점',
    try_content TEXT COMMENT 'Try - 시도할 것',
    learning_content TEXT COMMENT '학습 내용',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '작성일시',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    UNIQUE KEY unique_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='회고';

-- ========================================
-- 스키마 생성 완료
-- ========================================
