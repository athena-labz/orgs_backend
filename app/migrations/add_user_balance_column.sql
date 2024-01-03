CREATE TABLE IF NOT EXISTS user_balance (
    id SERIAL PRIMARY KEY,
    amount BIGINT NOT NULL,
    is_claimed BOOLEAN DEFAULT FALSE NOT NULL,
    is_error BOOLEAN DEFAULT FALSE NOT NULL,
    claim_error VARCHAR NULL,
    user_member_id INT REFERENCES organization_membership(id) ON DELETE CASCADE,
    balance_date TIMESTAMPTZ DEFAULT current_timestamp NOT NULL,
    claim_date TIMESTAMPTZ NULL
);
