-- ============================================================
-- EKBMS — Enterprise Knowledge Base Management System
-- SQLite schema + seed data
-- ============================================================
-- The backend auto-creates these tables via SQLAlchemy on startup.
-- This file is provided for evaluators / DBAs who want to inspect
-- the schema or rebuild the DB independently.
--
-- Apply with:
--     sqlite3 database/ekbms.db < database/schema.sql
-- ============================================================

PRAGMA foreign_keys = ON;

-- Drop in dependency-safe order (children first)
DROP TABLE IF EXISTS approval_logs;
DROP TABLE IF EXISTS bookmarks;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS attachments;
DROP TABLE IF EXISTS article_tags;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- ------------------------------------------------------------
-- Roles
-- ------------------------------------------------------------
CREATE TABLE roles (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  VARCHAR(50) NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- Users
-- ------------------------------------------------------------
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(200) NOT NULL UNIQUE,
    role_id     INTEGER NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
CREATE INDEX idx_users_email ON users(email);

-- ------------------------------------------------------------
-- Categories (hierarchical, parent_id self-reference)
-- ------------------------------------------------------------
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(120) NOT NULL,
    parent_id   INTEGER NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, parent_id),
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- ------------------------------------------------------------
-- Tags
-- ------------------------------------------------------------
CREATE TABLE tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  VARCHAR(60) NOT NULL UNIQUE
);
CREATE INDEX idx_tags_name ON tags(name);

-- ------------------------------------------------------------
-- Articles
-- ------------------------------------------------------------
CREATE TABLE articles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        VARCHAR(200) NOT NULL,
    content      TEXT NOT NULL,
    category_id  INTEGER NULL,
    author_id    INTEGER NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'draft'
                 CHECK (status IN ('draft','pending','approved','rejected','archived')),
    view_count   INTEGER NOT NULL DEFAULT 0,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id)   REFERENCES users(id)
);
CREATE INDEX idx_articles_title    ON articles(title);
CREATE INDEX idx_articles_status   ON articles(status);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_author   ON articles(author_id);

-- ------------------------------------------------------------
-- Article <-> Tag (many-to-many)
-- ------------------------------------------------------------
CREATE TABLE article_tags (
    article_id INTEGER NOT NULL,
    tag_id     INTEGER NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)     REFERENCES tags(id)     ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Attachments
-- ------------------------------------------------------------
CREATE TABLE attachments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id    INTEGER NOT NULL,
    file_name     VARCHAR(255) NOT NULL,
    stored_name   VARCHAR(255) NOT NULL,
    content_type  VARCHAR(100),
    size_bytes    INTEGER NOT NULL DEFAULT 0,
    uploaded_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);
CREATE INDEX idx_attachments_article ON attachments(article_id);

-- ------------------------------------------------------------
-- Comments
-- ------------------------------------------------------------
CREATE TABLE comments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    body        TEXT NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)
);
CREATE INDEX idx_comments_article ON comments(article_id);

-- ------------------------------------------------------------
-- Ratings (1-5, one per user/article)
-- ------------------------------------------------------------
CREATE TABLE ratings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    stars       INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (article_id, user_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- ------------------------------------------------------------
-- Bookmarks (unique per user/article)
-- ------------------------------------------------------------
CREATE TABLE bookmarks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (article_id, user_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- ------------------------------------------------------------
-- Approval logs (audit trail)
-- ------------------------------------------------------------
CREATE TABLE approval_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    action      VARCHAR(20) NOT NULL CHECK (action IN ('approved','rejected')),
    comment     TEXT,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id)  REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);
CREATE INDEX idx_approval_article ON approval_logs(article_id);

-- ============================================================
-- Seed data
-- ============================================================

-- Roles
INSERT INTO roles (id, name) VALUES
    (1, 'Admin'),
    (2, 'Author'),
    (3, 'Reviewer'),
    (4, 'Employee');

-- Users (one per role, plus an extra Author and Employee)
INSERT INTO users (id, name, email, role_id) VALUES
    (1, 'Aarav Admin',     'admin@ekbms.com',    1),
    (2, 'Priya Author',    'priya.author@ekbms.com', 2),
    (3, 'Rohan Author',    'rohan.author@ekbms.com', 2),
    (4, 'Neha Reviewer',   'neha.reviewer@ekbms.com', 3),
    (5, 'Vikram Employee', 'vikram@ekbms.com',    4),
    (6, 'Sneha Employee',  'sneha@ekbms.com',     4);

-- Categories (top-level + nested children to demonstrate hierarchy)
INSERT INTO categories (id, name, parent_id) VALUES
    (1, 'HR Policies',        NULL),
    (2, 'IT Support',         NULL),
    (3, 'Finance',            NULL),
    (4, 'Operations',         NULL),
    (5, 'Training Materials', NULL),
    (6, 'Leave Policies',     1),    -- HR > Leave Policies
    (7, 'Onboarding',         1),    -- HR > Onboarding
    (8, 'Networking',         2),    -- IT > Networking
    (9, 'VPN',                8),    -- IT > Networking > VPN
    (10,'Hardware',           2),    -- IT > Hardware
    (11,'Expense Reports',    3);    -- Finance > Expense Reports

-- Tags
INSERT INTO tags (id, name) VALUES
    (1, 'leave'),
    (2, 'wfh'),
    (3, 'vpn'),
    (4, 'troubleshooting'),
    (5, 'onboarding'),
    (6, 'expense'),
    (7, 'policy'),
    (8, 'sop'),
    (9, 'training'),
    (10,'security');

-- Articles (mix of statuses to exercise the workflow)
INSERT INTO articles (id, title, content, category_id, author_id, status, view_count) VALUES
    (1, 'Annual Leave Policy 2026',
        'Employees are entitled to 24 days of paid annual leave per calendar year. Requests must be filed in the HR portal at least 7 working days in advance. Carry-over of up to 5 days is permitted with manager approval.',
        6, 2, 'approved', 142),
    (2, 'Work-From-Home Guidelines',
        'Hybrid employees may work from home up to 3 days per week. Ensure stable internet (10 Mbps+), be reachable on Teams/Slack during core hours, and follow the standard security checklist.',
        1, 2, 'approved', 98),
    (3, 'VPN Setup — Windows',
        'Step 1: Download the GlobalProtect installer from the IT portal. Step 2: Run as administrator. Step 3: Enter portal address vpn.ekbms.local. Step 4: Authenticate with your AD credentials. Step 5: Test by browsing an internal-only resource.',
        9, 3, 'approved', 211),
    (4, 'New Hire Onboarding Checklist',
        'Day 1: Laptop pickup, ID card, access provisioning. Week 1: Mandatory training (security, code of conduct). Week 2: Team intros + first ticket assignment. End of month: 30-day check-in with manager.',
        7, 2, 'approved', 73),
    (5, 'Expense Report Submission SOP',
        'Submit receipts through the Finance portal within 30 days of incurring the expense. Attach scanned copies of all receipts > Rs. 500. Approvals route to your reporting manager, then Finance.',
        11, 3, 'approved', 54),
    (6, 'Laptop Issue Troubleshooting',
        'If laptop fails to boot: 1) Hold power for 30s, 2) Try external monitor, 3) Check for amber LED. If still failing, raise an IT ticket with serial number and amber/red LED status.',
        10, 3, 'pending', 0),
    (7, 'Information Security Training — Q2',
        'Mandatory online module covering phishing, password hygiene, data classification, and incident reporting. Complete by end of quarter to avoid access suspension.',
        5, 2, 'pending', 0),
    (8, 'Draft: Reimbursement Policy v2',
        'Working draft for the updated reimbursement policy. To be finalized after Finance review.',
        3, 3, 'draft', 0);

-- Article <-> Tag links
INSERT INTO article_tags (article_id, tag_id) VALUES
    (1, 1), (1, 7),               -- Leave Policy: leave, policy
    (2, 2), (2, 7),               -- WFH: wfh, policy
    (3, 3), (3, 4), (3, 8),       -- VPN: vpn, troubleshooting, sop
    (4, 5), (4, 8),               -- Onboarding: onboarding, sop
    (5, 6), (5, 8),               -- Expense: expense, sop
    (6, 4),                       -- Laptop: troubleshooting
    (7, 9), (7, 10),              -- Security training: training, security
    (8, 6), (8, 7);               -- Reimbursement draft: expense, policy

-- Sample comments
INSERT INTO comments (article_id, user_id, body) VALUES
    (1, 5, 'Very helpful — can we get a quick FAQ for sandwich leaves?'),
    (3, 6, 'Worked perfectly on my Windows 11 machine. Thanks!'),
    (3, 5, 'Does this work for macOS too?');

-- Sample ratings
INSERT INTO ratings (article_id, user_id, stars) VALUES
    (1, 5, 5),
    (1, 6, 4),
    (2, 5, 4),
    (3, 5, 5),
    (3, 6, 5),
    (4, 6, 4),
    (5, 5, 3);

-- Sample bookmarks
INSERT INTO bookmarks (article_id, user_id) VALUES
    (1, 5),
    (3, 5),
    (3, 6);

-- One approval log for the previously approved VPN article (illustrative)
INSERT INTO approval_logs (article_id, reviewer_id, action, comment) VALUES
    (3, 4, 'approved', 'Steps verified end-to-end on a fresh Windows install.');
