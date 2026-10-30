-- =============================================================================
-- EVENTFLOW — DỮ LIỆU MẪU KHỞI TẠO HỆ THỐNG (SEED DATA)
-- FILE: database/seed_data.sql
-- MÔ TẢ: Khởi tạo dữ liệu người dùng, cơ sở vật chất, thiết bị và cấu hình tham số
-- MẬT KHẨU MẶC ĐỊNH CHO TẤT CẢ TÀI KHOẢN: 123456
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. TÀI KHOẢN NGƯỜI DÙNG DEMO (13 USERS)
-- Mã hash bcrypt của mật khẩu "123456": $2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
-- -----------------------------------------------------------------------------

INSERT INTO users (id, email, password_hash, full_name, phone, role, department, is_active) VALUES
-- Nhóm tài khoản chuẩn trường DUE (@due.edu.vn)
('u-admin-due',  'admin@due.edu.vn',      '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Quản Trị Hệ Thống DUE',       '0905678901', 'ADMIN',       'Trung tâm CNTT DUE',                   TRUE),
('u-btc-due',    'btc@due.edu.vn',        '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Ban Tổ Chức DUE (CLB KNDN)',   '0905123456', 'BTC',         'CLB Kỹ Năng Doanh Nhân',               TRUE),
('u-bcn-due',    'bcn@due.edu.vn',        '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'PGS.TS. Lê Văn Cường',         '0905234567', 'BCN_KHOA',    'Khoa Thương mại Điện tử',              TRUE),
('u-doan-due',   'doantruong@due.edu.vn', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'ThS. Phạm Thị Dung',          '0905345678', 'DOAN_TRUONG', 'Văn phòng Đoàn Thanh niên - Hội SV',   TRUE),
('u-csvc-due',   'csvc@due.edu.vn',       '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Nguyễn Hữu Em',               '0905456789', 'CSVC',        'Phòng Cơ sở vật chất & Thiết bị',      TRUE),
('u-khtc-due',   'khtc@due.edu.vn',       '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Trần Văn Phúc',               '0905567890', 'KHTC',        'Phòng Kế hoạch - Tài chính',           TRUE),

-- Nhóm tài khoản demo định danh (@eventflow.vn)
('u-admin',      'admin@eventflow.vn',    '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Lê Hoàng Admin',              '0905111222', 'ADMIN',       'Trung tâm Công nghệ Thông tin',        TRUE),
('u-btc1',       'btc1@eventflow.vn',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Nguyễn Văn An',               '0914222333', 'BTC',         'CLB Tin học DUE (IT Club)',            TRUE),
('u-btc2',       'btc2@eventflow.vn',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Trần Thị Bình',               '0935333444', 'BTC',         'Liên Chi đoàn Khoa QTKD',              TRUE),
('u-bcn',        'bcnkhoa@eventflow.vn',  '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'TS. Nguyễn Hữu Dũng',         '0903555666', 'BCN_KHOA',    'Ban Chủ nhiệm Khoa Quản trị Kinh doanh', TRUE),
('u-doan',       'doantruong@eventflow.vn','$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Đoàn Trường Đại học Kinh tế', '0905777888', 'DOAN_TRUONG', 'Văn phòng Đoàn - Hội DUE',           TRUE),
('u-csvc',       'csvc@eventflow.vn',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Cán bộ Quản lý CSVC',         '0913888999', 'CSVC',        'Bộ phận Quản lý CSVC & Hội trường',   TRUE),
('u-khtc',       'khtc@eventflow.vn',     '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', 'Chuyên viên Kế hoạch Tài chính','0905999000', 'KHTC',       'Tổ Thẩm tra Quyết toán KHTC',         TRUE)
ON CONFLICT (id) DO UPDATE 
SET email = EXCLUDED.email, full_name = EXCLUDED.full_name, role = EXCLUDED.role, department = EXCLUDED.department;

-- -----------------------------------------------------------------------------
-- 2. DANH MỤC HỘI TRƯỜNG & PHÒNG CHỨC NĂNG (6 FACILITIES)
-- -----------------------------------------------------------------------------

INSERT INTO facilities (id, code, name, location, capacity, type, description, amenities, is_active) VALUES
('fac-1', 'HT-A', 'Hội trường A (Khu nhà Đa năng)', 'Tầng 2, Tòa nhà Đa năng A1', 500, 'HALL', 'Hội trường lớn nhất trường, phục vụ đại hội, hội thảo quốc tế và biểu diễn nghệ thuật quy mô lớn.', '["Màn hình LED 300 inch", "Âm thanh vòm Array", "Micro cổ ngỗng", "Máy lạnh trung tâm", "Hệ thống ánh sáng sân khấu"]', TRUE),
('fac-2', 'HT-B', 'Hội trường B (Khu Giảng đường C)', 'Tầng 1, Nhà C', 300, 'HALL', 'Hội trường tầm trung, lý tưởng cho tọa đàm chuyên đề, chung kết cuộc thi học thuật khoa.', '["Máy chiếu Laser công suất lớn", "Âm thanh hội thảo", "Ghế nệm có bàn gập", "Wifi phủ sóng cao"]', TRUE),
('fac-3', 'P-DN-E', 'Phòng Đa năng E201', 'Tầng 2, Nhà E', 150, 'ROOM', 'Không gian mở đa năng, có bàn ghế di động, thích hợp workshop tương tác, sinh hoạt CLB.', '["Bàn ghế module linh hoạt", "2 Màn hình TV 85 inch", "Bảng tương tác", "Bục phát biểu"]', TRUE),
('fac-4', 'SANH-A', 'Sảnh chính Tòa nhà A', 'Tầng trệt Tòa nhà A', 400, 'LOBBY', 'Khu vực tiền sảnh rộng rãi, thuận tiện triển lãm sản phẩm, ngày hội việc làm và check-in sự kiện.', '["Nguồn điện 3 pha cho gian hàng", "Bảng thông tin điện tử", "Khu vực backdrop ngoài trời"]', TRUE),
('fac-5', 'SAN-BONG', 'Khu phức hợp Thể thao ngoài trời', 'Khuôn viên phía Đông', 600, 'OUTDOOR', 'Sân thể thao đa năng, phục vụ ngày hội thể thao sinh viên, hội thao và cắm trại.', '["Hệ thống chiếu sáng ban đêm", "Khán đài có mái che", "Khu vệ sinh riêng", "Khu vực y tế"]', TRUE),
('fac-6', 'PH-BGH', 'Phòng họp Ban Giám hiệu', 'Tầng 3, Nhà Hiệu bộ A2', 40, 'ROOM', 'Phòng họp cấp cao cho các lễ ký kết thỏa thuận hợp tác, tiếp đón đoàn đối tác quan trọng.', '["Hệ thống họp trực tuyến Cisco", "Mic hội nghị từng vị trí", "Màn hình tương tác 4K"]', TRUE)
ON CONFLICT (id) DO UPDATE 
SET name = EXCLUDED.name, location = EXCLUDED.location, capacity = EXCLUDED.capacity, amenities = EXCLUDED.amenities;

-- -----------------------------------------------------------------------------
-- 3. DANH MỤC THIẾT BỊ SỰ KIỆN (5 EQUIPMENT)
-- -----------------------------------------------------------------------------

INSERT INTO equipment (id, code, name, type, total_quantity, description, condition, is_active) VALUES
('eq-1', 'AT-L01', 'Hệ thống Loa di động Array 2000W', 'SOUND', 4, 'Bộ 2 loa cột công suất lớn kèm mixer số 16 line cho sự kiện ngoài trời', 'EXCELLENT', TRUE),
('eq-2', 'MC-W02', 'Bộ Micro không dây cầm tay Shure GLX', 'SOUND', 12, 'Micro dải tần UHF chống hú tốt, tầm hoạt động 80m', 'GOOD', TRUE),
('eq-3', 'MC-C03', 'Micro cài áo / Headset MC-03', 'SOUND', 6, 'Phù hợp diễn giả thuyết trình, MC hoạt náo', 'GOOD', TRUE),
('eq-4', 'AS-LED', 'Dàn Đèn Par LED 54 bóng RGBW', 'LIGHTING', 16, 'Đèn chiếu sáng sân khấu đổi màu đa hiệu ứng', 'GOOD', TRUE),
('eq-5', 'BD-UHF', 'Bộ đàm bảo vệ & điều phối nội bộ', 'OTHER', 15, 'Bộ đàm cự ly 1.5km phục vụ ban hậu cần và an ninh', 'GOOD', TRUE)
ON CONFLICT (id) DO UPDATE 
SET name = EXCLUDED.name, total_quantity = EXCLUDED.total_quantity, condition = EXCLUDED.condition;

-- -----------------------------------------------------------------------------
-- 4. THAM SỐ CẤU HÌNH HỆ THỐNG (SYSTEM SETTINGS)
-- -----------------------------------------------------------------------------

INSERT INTO system_settings (id, key, value, description, category) VALUES
('set-1', 'FACILITY_HOLD_HOURS', '48', 'Thời gian giữ chỗ tạm thời (giờ) trước khi tự hủy nếu chưa được duyệt', 'WORKFLOW'),
('set-2', 'SPECIAL_BUDGET_THRESHOLD', '50000000', 'Hạn mức ngân sách (VNĐ) yêu cầu phê duyệt đặc biệt từ Ban Giám hiệu', 'FINANCE'),
('set-3', 'MAX_EVENT_DAYS_IN_ADVANCE', '60', 'Số ngày nộp hồ sơ tối đa trước thời điểm diễn ra sự kiện', 'PLANNING'),
('set-4', 'MIN_EVENT_DAYS_IN_ADVANCE', '7', 'Số ngày nộp hồ sơ tối thiểu trước thời điểm diễn ra sự kiện', 'PLANNING'),
('set-5', 'UNIVERSITY_NAME', 'Trường Đại học Kinh tế – Đại học Đà Nẵng (DUE)', 'Tên chính thức của đơn vị quản trị hệ thống', 'SYSTEM')
ON CONFLICT (key) DO UPDATE 
SET value = EXCLUDED.value, description = EXCLUDED.description;
