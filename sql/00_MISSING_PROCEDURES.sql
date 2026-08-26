-- file: sql/00_MISSING_PROCEDURES.sql
-- Chạy file này trong SQL Server Management Studio
-- Database: QL_BANHANG_SAUBANH
-- Tạo các Stored Procedure còn thiếu để app Flask hoạt động
-- ================================================================

USE QL_BANHANG_SAUBANH;
GO

-- ================================================================
-- 1. View nhà cung cấp (nếu chưa có)
-- ================================================================
IF NOT EXISTS (SELECT 1 FROM sys.views WHERE name = 'V_NHACUNGCAP')
BEGIN
    EXEC('CREATE VIEW V_NHACUNGCAP AS
          SELECT MANCC, TENNCC, DIENTHOAI, DIACHI, EMAIL
          FROM NHACUNGCAP')
END
GO

-- ================================================================
-- 2. usp_THEM_SANPHAM
-- ================================================================
CREATE OR ALTER PROCEDURE usp_THEM_SANPHAM
    @MASP    NVARCHAR(20),
    @TENSP   NVARCHAR(100),
    @MALOAI  NVARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
            IF EXISTS (SELECT 1 FROM SANPHAM WHERE MASP = @MASP)
                THROW 50001, N'Mã sản phẩm đã tồn tại.', 1;

            INSERT INTO SANPHAM (MASP, TENSP, MALOAI)
            VALUES (@MASP, @TENSP, @MALOAI);
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 3. usp_THEM_SANPHAM_CHITIET
-- ================================================================
CREATE OR ALTER PROCEDURE usp_THEM_SANPHAM_CHITIET
    @MASPCT  NVARCHAR(30),
    @MASP    NVARCHAR(20),
    @MAMAU   NVARCHAR(20) = NULL,
    @MASIZE  NVARCHAR(10) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
            IF EXISTS (SELECT 1 FROM SANPHAM_CHITIET WHERE MASPCT = @MASPCT)
                THROW 50002, N'Mã sản phẩm chi tiết đã tồn tại.', 1;

            INSERT INTO SANPHAM_CHITIET (MASPCT, MASP, MAMAU, MASIZE)
            VALUES (@MASPCT, @MASP, @MAMAU, @MASIZE);
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 4. usp_THEM_BANGGIA
-- ================================================================
CREATE OR ALTER PROCEDURE usp_THEM_BANGGIA
    @MASPCT       NVARCHAR(30),
    @GIA_BAN      DECIMAL(18,2),
    @GIA_NHAP     DECIMAL(18,2),
    @NGAY_AP_DUNG DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @NGAY_AP_DUNG IS NULL SET @NGAY_AP_DUNG = CAST(GETDATE() AS DATE);
    BEGIN TRY
        BEGIN TRANSACTION;
            INSERT INTO BANGGIA (MASPCT, GIA_BAN, GIA_NHAP, NGAY_AP_DUNG)
            VALUES (@MASPCT, @GIA_BAN, @GIA_NHAP, @NGAY_AP_DUNG);
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 5. usp_CAPNHAT_KHACHHANG
-- ================================================================
CREATE OR ALTER PROCEDURE usp_CAPNHAT_KHACHHANG
    @MAKH    NVARCHAR(20),
    @TENKH   NVARCHAR(100),
    @SDT     NVARCHAR(15) = NULL,
    @DIACHI  NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
            UPDATE KHACHHANG
            SET TENKH  = @TENKH,
                SDT    = @SDT,
                DIACHI = @DIACHI
            WHERE MAKH = @MAKH;

            IF @@ROWCOUNT = 0
                THROW 50003, N'Không tìm thấy khách hàng.', 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 6. usp_THEM_NHACUNGCAP
-- ================================================================
CREATE OR ALTER PROCEDURE usp_THEM_NHACUNGCAP
    @MANCC      NVARCHAR(20),
    @TENNCC     NVARCHAR(100),
    @DIENTHOAI  NVARCHAR(15) = NULL,
    @DIACHI     NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
            IF EXISTS (SELECT 1 FROM NHACUNGCAP WHERE MANCC = @MANCC)
                THROW 50004, N'Mã nhà cung cấp đã tồn tại.', 1;

            INSERT INTO NHACUNGCAP (MANCC, TENNCC, DIENTHOAI, DIACHI)
            VALUES (@MANCC, @TENNCC, @DIENTHOAI, @DIACHI);
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 7. usp_CAPNHAT_NHACUNGCAP
-- ================================================================
CREATE OR ALTER PROCEDURE usp_CAPNHAT_NHACUNGCAP
    @MANCC      NVARCHAR(20),
    @TENNCC     NVARCHAR(100),
    @DIENTHOAI  NVARCHAR(15) = NULL,
    @DIACHI     NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
            UPDATE NHACUNGCAP
            SET TENNCC    = @TENNCC,
                DIENTHOAI = @DIENTHOAI,
                DIACHI    = @DIACHI
            WHERE MANCC = @MANCC;

            IF @@ROWCOUNT = 0
                THROW 50005, N'Không tìm thấy nhà cung cấp.', 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK;
        THROW;
    END CATCH
END
GO

-- ================================================================
-- 8. usp_LAY_CHITIET_HOADON_BAN
-- ================================================================
CREATE OR ALTER PROCEDURE usp_LAY_CHITIET_HOADON_BAN
    @MAHDB CHAR(10)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT *
    FROM V_HOADON_BAN_CHITIET
    WHERE MAHDB = @MAHDB;
END
GO

PRINT N'=== Tạo thành công tất cả Stored Procedure bổ sung ===';
GO
