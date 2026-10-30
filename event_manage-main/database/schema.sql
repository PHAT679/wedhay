-- =============================================================================
-- EVENTFLOW — HỆ THỐNG QUẢN LÝ QUY TRÌNH TỔ CHỨC SỰ KIỆN (DUE)
-- FILE: database/schema.sql
-- MÔ TẢ: Khởi tạo toàn bộ cấu trúc bảng, chỉ mục, khóa ngoại và ràng buộc RBAC
-- TƯƠNG THÍCH: PostgreSQL 14+, SQLite, MySQL 8+
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. BẢNG PHÂN QUYỀN HỆ THỐNG (RBAC CORE)
-- -----------------------------------------------------------------------------

-- Bảng Vai trò (Roles)
CREATE TABLE IF NOT EXISTS roles (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    priority INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Quyền hạn chi tiết (Permissions)
CREATE TABLE IF NOT EXISTS permissions (
    code VARCHAR(100) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    module VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Ánh xạ Vai trò - Quyền hạn (Role-Permission Mapping)
CREATE TABLE IF NOT EXISTS role_permissions (
    role_code VARCHAR(50) NOT NULL,
    permission_code VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_code, permission_code),
    FOREIGN KEY (role_code) REFERENCES roles(code) ON DELETE CASCADE,
    FOREIGN KEY (permission_code) REFERENCES permissions(code) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 2. TÀI KHOẢN NGƯỜI DÙNG (USERS)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    role VARCHAR(50) NOT NULL,
    department VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role) REFERENCES roles(code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- -----------------------------------------------------------------------------
-- 3. HỒ SƠ SỰ KIỆN & QUY TRÌNH (EVENTS & WORKFLOW)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(64) PRIMARY KEY,
    event_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    objectives TEXT,
    target_audience VARCHAR(255),
    expected_attendees INT DEFAULT 0,
    organizing_unit VARCHAR(150) NOT NULL,
    contact_person VARCHAR(150),
    contact_email VARCHAR(150),
    contact_phone VARCHAR(30),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    setup_time TIMESTAMP,
    teardown_time TIMESTAMP,
    preferred_venue VARCHAR(255),
    plan_content TEXT,
    safety_plan TEXT,
    communication_plan TEXT,
    
    -- Trạng thái quy trình 9 giai đoạn (34 states)
    status VARCHAR(60) DEFAULT 'DRAFT',
    permit_status VARCHAR(40) DEFAULT 'PENDING',
    facility_status VARCHAR(40) DEFAULT 'PENDING',
    inspection_status VARCHAR(40) DEFAULT 'PENDING',
    settlement_status VARCHAR(40) DEFAULT 'PENDING',
    report_status VARCHAR(40) DEFAULT 'PENDING',
    current_version INT DEFAULT 1,
    
    created_by_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_events_code ON events(event_code);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_creator ON events(created_by_id);
CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date);

-- Lịch sử các phiên bản hồ sơ (Event Versions)
CREATE TABLE IF NOT EXISTS event_versions (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    version INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    objectives TEXT,
    plan_content TEXT,
    budget_data TEXT,
    change_note TEXT,
    changed_by VARCHAR(64),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_event_versions_event ON event_versions(event_id, version);

-- Kịch bản chi tiết chương trình (Agenda / Schedule)
CREATE TABLE IF NOT EXISTS event_schedule_items (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    time_slot VARCHAR(100) NOT NULL,
    activity VARCHAR(255) NOT NULL,
    responsible VARCHAR(150),
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_schedule_event ON event_schedule_items(event_id, sort_order);

-- Dự toán kinh phí & Thực chi (Budget Items)
CREATE TABLE IF NOT EXISTS budget_items (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    category VARCHAR(100) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    quantity INT DEFAULT 1,
    unit_price DECIMAL(15, 2) DEFAULT 0,
    total_price DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    actual_quantity INT NULL,
    actual_price DECIMAL(15, 2) NULL,
    actual_total DECIMAL(15, 2) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_budget_event ON budget_items(event_id);

-- Quyết định phê duyệt qua các cấp (Approval Decisions)
CREATE TABLE IF NOT EXISTS approval_decisions (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    stage VARCHAR(50) NOT NULL,          -- FACULTY_REVIEW, UNIVERSITY_REVIEW, FACILITY_REVIEW, FINANCE_REVIEW
    decision VARCHAR(50) NOT NULL,       -- APPROVED, REJECTED, REVISION_REQUESTED
    comments TEXT,
    reason TEXT,
    version INT DEFAULT 1,
    decided_by_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (decided_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_approval_event ON approval_decisions(event_id, stage);

-- Nhật ký luân chuyển hồ sơ (Audit Workflow History)
CREATE TABLE IF NOT EXISTS workflow_histories (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    from_status VARCHAR(60) NOT NULL,
    to_status VARCHAR(60) NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor_id VARCHAR(64),
    actor_name VARCHAR(150),
    actor_role VARCHAR(50),
    comments TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_workflow_history_event ON workflow_histories(event_id, created_at);

-- Tài liệu đính kèm (Attachments)
CREATE TABLE IF NOT EXISTS attachments (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    uploaded_by_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 4. CƠ SỞ VẬT CHẤT & ĐẶT CHỖ (FACILITIES & BOOKINGS)
-- -----------------------------------------------------------------------------

-- Danh mục Hội trường & Phòng (Facilities)
CREATE TABLE IF NOT EXISTS facilities (
    id VARCHAR(64) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(200),
    capacity INT DEFAULT 0,
    type VARCHAR(50) NOT NULL,          -- HALL, ROOM, LOBBY, OUTDOOR
    description TEXT,
    amenities TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Danh mục Thiết bị sự kiện (Equipment)
CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(64) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL,          -- SOUND, LIGHTING, SCREEN, FURNITURE
    total_quantity INT DEFAULT 1,
    description TEXT,
    condition VARCHAR(50) DEFAULT 'GOOD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lịch Đặt chỗ Cơ sở vật chất (Resource Bookings)
CREATE TABLE IF NOT EXISTS resource_bookings (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    facility_id VARCHAR(64) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    setup_time TIMESTAMP,
    teardown_time TIMESTAMP,
    expected_attendees INT,
    purpose TEXT,
    special_requests TEXT,
    alternative_option TEXT,
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, CONFIRMED, CANCELLED, REJECTED
    confirmed_by_id VARCHAR(64),
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_bookings_facility_time ON resource_bookings(facility_id, start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_bookings_event ON resource_bookings(event_id);

-- Thiết bị được đặt kèm theo phòng (Booking Items)
CREATE TABLE IF NOT EXISTS resource_booking_items (
    id VARCHAR(64) PRIMARY KEY,
    booking_id VARCHAR(64) NOT NULL,
    equipment_id VARCHAR(64) NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES resource_bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 5. BÀN GIAO, NGHIỆM THU VÀ XỬ LÝ SỰ CỐ (HANDOVER & INSPECTION)
-- -----------------------------------------------------------------------------

-- Biên bản bàn giao trước sự kiện (Handover Records)
CREATE TABLE IF NOT EXISTS handover_records (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    type VARCHAR(50) NOT NULL,            -- PRE_EVENT, POST_EVENT
    handover_by_id VARCHAR(64) NOT NULL,
    received_by_id VARCHAR(64),
    facility_condition TEXT,
    equipment_list TEXT,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, SIGNED, COMPLETED
    handover_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (handover_by_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (received_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- Biên bản nghiệm thu & hoàn trả sau sự kiện (Return Inspections)
CREATE TABLE IF NOT EXISTS return_inspections (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    inspected_by_id VARCHAR(64) NOT NULL,
    facility_condition TEXT,
    equipment_condition TEXT,
    overall_result VARCHAR(50) DEFAULT 'PENDING', -- PASSED, PASSED_WITH_ISSUES, FAILED
    notes TEXT,
    inspected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (inspected_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- Biên bản sự cố hư hỏng (Incident Reports)
CREATE TABLE IF NOT EXISTS incident_reports (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    reported_by_id VARCHAR(64) NOT NULL,
    type VARCHAR(50) NOT NULL,            -- EQUIPMENT_DAMAGE, FACILITY_DAMAGE, DELAY, SAFETY
    description TEXT NOT NULL,
    severity VARCHAR(50) DEFAULT 'MEDIUM',-- LOW, MEDIUM, HIGH, CRITICAL
    resolution TEXT,
    status VARCHAR(50) DEFAULT 'OPEN',    -- OPEN, INVESTIGATING, RESOLVED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 6. QUYẾT TOÁN TÀI CHÍNH (FINANCIAL SETTLEMENT)
-- -----------------------------------------------------------------------------

-- Hồ sơ quyết toán kinh phí (Settlements)
CREATE TABLE IF NOT EXISTS settlements (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL,
    total_budgeted DECIMAL(15, 2) DEFAULT 0,
    total_actual DECIMAL(15, 2) DEFAULT 0,
    difference DECIMAL(15, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'DRAFT',   -- DRAFT, SUBMITTED, APPROVED, REJECTED, REVISION_REQUESTED
    submitted_by_id VARCHAR(64),
    submitted_at TIMESTAMP,
    reviewed_by_id VARCHAR(64),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Mục kê chi tiết quyết toán (Settlement Items)
CREATE TABLE IF NOT EXISTS settlement_items (
    id VARCHAR(64) PRIMARY KEY,
    settlement_id VARCHAR(64) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    budgeted_amount DECIMAL(15, 2) DEFAULT 0,
    actual_amount DECIMAL(15, 2) DEFAULT 0,
    difference DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (settlement_id) REFERENCES settlements(id) ON DELETE CASCADE
);

-- Chứng từ, hóa đơn VAT đính kèm (Financial Documents)
CREATE TABLE IF NOT EXISTS financial_documents (
    id VARCHAR(64) PRIMARY KEY,
    settlement_id VARCHAR(64) NOT NULL,
    document_type VARCHAR(100) NOT NULL, -- VAT_INVOICE, RECEIPT, CONTRACT, BANK_TRANSFER
    document_number VARCHAR(100),
    amount DECIMAL(15, 2),
    description TEXT,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (settlement_id) REFERENCES settlements(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 7. BÁO CÁO TỔNG KẾT & THÔNG BÁO (REPORTS & NOTIFICATIONS)
-- -----------------------------------------------------------------------------

-- Báo cáo tổng kết sự kiện (Event Reports)
CREATE TABLE IF NOT EXISTS event_reports (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) UNIQUE NOT NULL,
    actual_attendees INT DEFAULT 0,
    summary TEXT,
    achievements TEXT,
    challenges TEXT,
    lessons_learned TEXT,
    recommendations TEXT,
    status VARCHAR(50) DEFAULT 'DRAFT',  -- DRAFT, SUBMITTED, ACCEPTED
    submitted_at TIMESTAMP,
    accepted_at TIMESTAMP,
    accepted_by VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Trung tâm thông báo (Notifications)
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    event_id VARCHAR(64),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,           -- INFO, WARNING, SUCCESS, URGENT
    category VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    link_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- Nhật ký kiểm toán bảo mật (Audit Logs)
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(64),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Cấu hình tham số hệ thống (System Settings)
CREATE TABLE IF NOT EXISTS system_settings (
    id VARCHAR(64) PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
