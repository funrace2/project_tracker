-- ========================================
-- Migration: Add User Authentication
-- ========================================
-- 사용자 인증 기능 추가를 위한 마이그레이션
-- ========================================

USE project_tracker;

-- ========================================
-- users 테이블 생성
-- ========================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '이메일 (로그인 ID)',
    password_hash VARCHAR(255) NOT NULL COMMENT '비밀번호 해시',
    username VARCHAR(100) NOT NULL COMMENT '사용자 이름',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '가입일시',
    last_login TIMESTAMP NULL COMMENT '마지막 로그인 시간',

    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='사용자';

-- ========================================
-- projects 테이블에 user_id 추가
-- ========================================
ALTER TABLE projects
ADD COLUMN user_id INT NULL COMMENT '사용자 ID (FK)' AFTER id,
ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
ADD INDEX idx_user (user_id);

-- ========================================
-- 마이그레이션 완료
-- ========================================
