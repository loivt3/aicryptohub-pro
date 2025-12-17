-- Insert admin user with password Clc@123**
-- Password hash is SHA256 of 'Clc@123**'

INSERT INTO admin_users (email, password_hash, name, role, is_active)
VALUES (
    'admin@aicryptohub.io',
    '8f6781953b5f6785854315f8924990ad5e8e998fa910d0d687f1eb5303597137d',
    'Super Admin',
    'admin',
    true
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = 'admin',
    is_active = true;

-- Verify the insert
SELECT id, email, name, role, is_active FROM admin_users WHERE email = 'admin@aicryptohub.io';
