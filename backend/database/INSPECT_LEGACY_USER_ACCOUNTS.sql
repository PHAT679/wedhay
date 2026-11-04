-- Read-only preflight for reconciling public.Users with my_due.User.
-- Do not run any import/update statement until the live columns and role mappings are reviewed.
-- PasswordHash, password reset tokens, and other credential material are never selected.

-- 1) Confirm live objects before running the shape-dependent queries below.
SELECT
  to_regclass('public."Users"') AS legacy_users,
  to_regclass('public."UserRoles"') AS legacy_user_roles,
  to_regclass('public."Roles"') AS legacy_roles,
  to_regclass('public."RolePermissions"') AS legacy_role_permissions,
  to_regclass('public."Permissions"') AS legacy_permissions,
  to_regclass('public."Departments"') AS legacy_departments,
  to_regclass('my_due."User"') AS application_users,
  to_regclass('my_due."LegacyIdentityMap"') AS legacy_identity_map;

-- 2) Inspect columns, SQL types, nullability, and defaults for the relevant live tables.
SELECT
  table_schema,
  table_name,
  ordinal_position,
  column_name,
  data_type,
  udt_name,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE (table_schema = 'public'
       AND table_name IN ('Users', 'UserRoles', 'Roles', 'RolePermissions', 'Permissions', 'Departments'))
   OR (table_schema = 'my_due'
       AND table_name IN ('User', 'LegacyIdentityMap', 'PasswordResetToken'))
ORDER BY table_schema, table_name, ordinal_position;

-- 3) Inspect primary keys, unique constraints, and foreign keys for those tables.
SELECT
  tc.table_schema,
  tc.table_name,
  tc.constraint_name,
  tc.constraint_type,
  kcu.column_name,
  ccu.table_schema AS referenced_schema,
  ccu.table_name AS referenced_table,
  ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_catalog = kcu.constraint_catalog
 AND tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
 AND tc.table_name = kcu.table_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
  ON tc.constraint_catalog = ccu.constraint_catalog
 AND tc.constraint_schema = ccu.constraint_schema
 AND tc.constraint_name = ccu.constraint_name
WHERE (tc.table_schema = 'public'
       AND tc.table_name IN ('Users', 'UserRoles', 'Roles', 'RolePermissions', 'Permissions', 'Departments'))
   OR (tc.table_schema = 'my_due'
       AND tc.table_name IN ('User', 'LegacyIdentityMap', 'PasswordResetToken'))
ORDER BY tc.table_schema, tc.table_name, tc.constraint_type, tc.constraint_name, kcu.ordinal_position;

-- 4) Inspect indexes, including unique indexes that are not declared as constraints.
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE (schemaname = 'public'
       AND tablename IN ('Users', 'UserRoles', 'Roles', 'RolePermissions', 'Permissions', 'Departments'))
   OR (schemaname = 'my_due'
       AND tablename IN ('User', 'LegacyIdentityMap', 'PasswordResetToken'))
ORDER BY schemaname, tablename, indexname;

-- 5) Find case/whitespace-insensitive duplicate legacy usernames.
-- This does not assume Username is an email address.
SELECT
  lower(btrim("Username")) AS normalized_username,
  count(*) AS account_count
FROM public."Users"
GROUP BY lower(btrim("Username"))
HAVING count(*) > 1
ORDER BY normalized_username;

-- 6) Review legacy identities with their current role and department mappings.
-- Username and display name are shown for manual email/identity verification.
-- PasswordHash is deliberately excluded.
SELECT
  u."UserId",
  u."Username",
  u."DisplayName",
  u."IsActive",
  u."DepartmentId",
  d."Code" AS department_code,
  d."Name" AS department_name,
  ur."RoleId",
  r."Code" AS legacy_role_code,
  r."Name" AS legacy_role_name
FROM public."Users" AS u
LEFT JOIN public."Departments" AS d
  ON d."DepartmentId" = u."DepartmentId"
LEFT JOIN public."UserRoles" AS ur
  ON ur."UserId" = u."UserId"
LEFT JOIN public."Roles" AS r
  ON r."RoleId" = ur."RoleId"
ORDER BY u."UserId", ur."RoleId";

-- 7) Review the permissions currently assigned to each legacy role.
SELECT
  r."RoleId",
  r."Code" AS legacy_role_code,
  r."Name" AS legacy_role_name,
  p."Code" AS permission_code,
  p."Description" AS permission_description
FROM public."Roles" AS r
LEFT JOIN public."RolePermissions" AS rp
  ON rp."RoleId" = r."RoleId"
LEFT JOIN public."Permissions" AS p
  ON p."PermissionId" = rp."PermissionId"
ORDER BY r."RoleId", p."Code";

-- 8) Find duplicate application emails after case/whitespace normalization.
SELECT
  lower(btrim("email")) AS normalized_email,
  count(*) AS account_count
FROM my_due."User"
GROUP BY lower(btrim("email"))
HAVING count(*) > 1
ORDER BY normalized_email;

-- 9) Compare only legacy usernames that are email-shaped with application emails.
-- A match is a conflict requiring review, not permission to overwrite either account.
SELECT
  legacy."UserId" AS legacy_user_id,
  legacy."Username" AS legacy_username,
  app."id" AS application_user_id,
  app."email" AS application_email,
  app."role" AS application_role,
  app."isActive" AS application_is_active
FROM public."Users" AS legacy
JOIN my_due."User" AS app
  ON lower(btrim(legacy."Username")) = lower(btrim(app."email"))
WHERE legacy."Username" ~* '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
ORDER BY lower(btrim(legacy."Username"));

-- 10) Inspect existing identity mappings only if query 1 confirms the table exists.
SELECT entity, legacyId, applicationId, verifiedAt
FROM my_due."LegacyIdentityMap"
WHERE entity IN ('User', 'UserActivation')
ORDER BY legacyId;
