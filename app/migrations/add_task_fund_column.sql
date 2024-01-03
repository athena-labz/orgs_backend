CREATE TABLE IF NOT EXISTS task_fund (
    id SERIAL PRIMARY KEY,
    amount BIGINT NOT NULL,
    user_member_id INT REFERENCES group_membership(id) ON DELETE CASCADE,
    task_id INT REFERENCES task(id) ON DELETE CASCADE
);