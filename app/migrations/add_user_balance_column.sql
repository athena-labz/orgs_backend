CREATE TABLE IF NOT EXISTS user_balance (
    id SERIAL PRIMARY KEY,
    amount BIGINT NOT NULL,
    is_claimed BOOLEAN DEFAULT FALSE,
    user_member_id INT REFERENCES organization_membership(id) ON DELETE CASCADE,
    balance_date TIMESTAMPTZ DEFAULT current_timestamp,
    claim_date TIMESTAMPTZ NULL
);
