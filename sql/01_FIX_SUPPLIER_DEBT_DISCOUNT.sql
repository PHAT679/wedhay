-- file: sql/01_FIX_SUPPLIER_DEBT_DISCOUNT.sql
-- Muc dich: Sua nghiep vu thanh toan cong no NCC theo so phai tra sau chiet khau.
-- Chay script nay trong SQL Server (DB: QL_BANHANG_SAUBANH)

USE QL_BANHANG_SAUBANH;
GO

CREATE OR ALTER PROCEDURE dbo.usp_THANH_TOAN_HDN
    @MATT NVARCHAR(20),
    @MAHDN NVARCHAR(20),
    @SOTIENTRA DECIMAL(15,2)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE
        @TONGTIEN DECIMAL(15,2),
        @CHIETKHAU DECIMAL(5,2),
        @PHAI_TRA DECIMAL(15,2),
        @DATRA DECIMAL(15,2);

    IF ISNULL(@SOTIENTRA, 0) <= 0
        RAISERROR(N'So tien thanh toan phai lon hon 0.', 16, 1);

    SELECT
        @TONGTIEN = ISNULL(TONGTIEN, 0),
        @CHIETKHAU = ISNULL(CHIETKHAU, 0)
    FROM HDNHAP WITH (UPDLOCK)
    WHERE MAHDN = @MAHDN;

    IF @TONGTIEN IS NULL
        RAISERROR(N'Hoa don nhap khong ton tai!', 16, 1);

    SET @PHAI_TRA = @TONGTIEN - (@TONGTIEN * @CHIETKHAU / 100);
    IF @PHAI_TRA < 0
        SET @PHAI_TRA = 0;

    SELECT
        @DATRA = ISNULL(SUM(SOTIENTRA), 0)
    FROM THANHTOAN
    WHERE MAHDN = @MAHDN;

    IF (@DATRA + @SOTIENTRA) > @PHAI_TRA
        RAISERROR(N'So tien thanh toan vuot qua so no con lai cua hoa don!', 16, 1);

    INSERT INTO THANHTOAN (MATT, MAHDN, SOTIENTRA)
    VALUES (@MATT, @MAHDN, @SOTIENTRA);
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_LAY_HDN_CONG_NO_THEO_NCC
    @MA_NCC NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH debt_by_invoice AS (
        SELECT
            h.MAHDN,
            h.MA_NCC,
            h.NGAYGIO_NK,
            ISNULL(h.TONGTIEN, 0) AS TONGTIEN,
            ISNULL(h.CHIETKHAU, 0) AS CHIETKHAU,
            ISNULL(h.TONGTIEN, 0) * ISNULL(h.CHIETKHAU, 0) / 100.0 AS TIEN_CHIET_KHAU,
            CASE
                WHEN ISNULL(h.TONGTIEN, 0) - (ISNULL(h.TONGTIEN, 0) * ISNULL(h.CHIETKHAU, 0) / 100.0) < 0
                    THEN 0
                ELSE ISNULL(h.TONGTIEN, 0) - (ISNULL(h.TONGTIEN, 0) * ISNULL(h.CHIETKHAU, 0) / 100.0)
            END AS PHAI_TRA,
            ISNULL(tt.DA_TRA, 0) AS DA_TRA
        FROM HDNHAP h
        LEFT JOIN (
            SELECT MAHDN, SUM(ISNULL(SOTIENTRA, 0)) AS DA_TRA
            FROM THANHTOAN
            GROUP BY MAHDN
        ) tt ON tt.MAHDN = h.MAHDN
        WHERE h.MA_NCC = @MA_NCC
    )
    SELECT
        d.MAHDN,
        d.MA_NCC,
        d.NGAYGIO_NK,
        d.TONGTIEN,
        d.CHIETKHAU,
        d.TIEN_CHIET_KHAU,
        d.PHAI_TRA,
        d.DA_TRA,
        CASE
            WHEN d.PHAI_TRA - d.DA_TRA < 0 THEN 0
            ELSE d.PHAI_TRA - d.DA_TRA
        END AS CONG_NO,
        CASE
            WHEN d.PHAI_TRA - d.DA_TRA <= 0 THEN N'Da thanh toan'
            ELSE N'Con no'
        END AS TRANG_THAI
    FROM debt_by_invoice d
    WHERE (d.PHAI_TRA - d.DA_TRA) > 0
    ORDER BY d.NGAYGIO_NK DESC, d.MAHDN DESC;
END
GO

CREATE OR ALTER PROCEDURE dbo.usp_LAY_CONG_NO_NHA_CUNG_CAP
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH invoice_debt AS (
        SELECT
            h.MA_NCC,
            CASE
                WHEN ISNULL(h.TONGTIEN, 0) - (ISNULL(h.TONGTIEN, 0) * ISNULL(h.CHIETKHAU, 0) / 100.0) < 0
                    THEN 0
                ELSE ISNULL(h.TONGTIEN, 0) - (ISNULL(h.TONGTIEN, 0) * ISNULL(h.CHIETKHAU, 0) / 100.0)
            END AS PHAI_TRA,
            ISNULL(tt.DA_TRA, 0) AS DA_TRA
        FROM HDNHAP h
        LEFT JOIN (
            SELECT MAHDN, SUM(ISNULL(SOTIENTRA, 0)) AS DA_TRA
            FROM THANHTOAN
            GROUP BY MAHDN
        ) tt ON tt.MAHDN = h.MAHDN
    ),
    debt_by_supplier AS (
        SELECT
            MA_NCC,
            SUM(PHAI_TRA) AS TONG_NO,
            SUM(DA_TRA) AS DA_TRA
        FROM invoice_debt
        GROUP BY MA_NCC
    )
    SELECT
        n.MA_NCC,
        n.TENNCC,
        ISNULL(d.TONG_NO, 0) AS TONG_NO,
        ISNULL(d.DA_TRA, 0) AS DA_TRA,
        CASE
            WHEN ISNULL(d.TONG_NO, 0) - ISNULL(d.DA_TRA, 0) < 0 THEN 0
            ELSE ISNULL(d.TONG_NO, 0) - ISNULL(d.DA_TRA, 0)
        END AS CONG_NO,
        CASE
            WHEN ISNULL(d.TONG_NO, 0) - ISNULL(d.DA_TRA, 0) <= 0 THEN N'Da thanh toan'
            ELSE N'Con no'
        END AS TRANG_THAI
    FROM NHACUNGCAP n
    LEFT JOIN debt_by_supplier d ON d.MA_NCC = n.MA_NCC
    ORDER BY CONG_NO DESC, n.MA_NCC;
END
GO
