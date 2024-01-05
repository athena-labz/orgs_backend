from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(16) NOT NULL,
    "email" VARCHAR(128) NOT NULL UNIQUE,
    "stake_address" VARCHAR(128) NOT NULL UNIQUE,
    "token" VARCHAR(256),
    "active" BOOL NOT NULL  DEFAULT True,
    "email_validation_string" VARCHAR(128) NOT NULL,
    "register_date" TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE INDEX IF NOT EXISTS "idx_user_stake_a_f8cc17" ON "user" ("stake_address");
CREATE TABLE IF NOT EXISTS "organization" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "identifier" VARCHAR(64) NOT NULL UNIQUE,
    "type" VARCHAR(16) NOT NULL,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "students_password" VARCHAR(32) NOT NULL,
    "teachers_password" VARCHAR(32) NOT NULL,
    "supervisor_password" VARCHAR(32) NOT NULL,
    "areas" JSONB NOT NULL,
    "creation_date" TIMESTAMPTZ NOT NULL,
    "admin_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_organizatio_identif_769714" ON "organization" ("identifier");
CREATE TABLE IF NOT EXISTS "group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "identifier" VARCHAR(64) NOT NULL,
    "source" VARCHAR(32) NOT NULL  DEFAULT 'user_created',
    "name" VARCHAR(128) NOT NULL,
    "creation_date" TIMESTAMPTZ NOT NULL,
    "organization_id" INT NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_group_identif_fda378" ON "group" ("identifier");
CREATE INDEX IF NOT EXISTS "idx_group_organiz_15f4b4" ON "group" ("organization_id");
CREATE TABLE IF NOT EXISTS "groupmembership" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "leader" BOOL NOT NULL  DEFAULT False,
    "accepted" BOOL NOT NULL  DEFAULT False,
    "rejected" BOOL NOT NULL  DEFAULT False,
    "invite_date" TIMESTAMPTZ NOT NULL,
    "group_id" INT NOT NULL REFERENCES "group" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "organizationmembership" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "area" VARCHAR(64),
    "membership_date" TIMESTAMPTZ NOT NULL,
    "organization_id" INT NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_organizatio_organiz_ddcbab" ON "organizationmembership" ("organization_id");
CREATE INDEX IF NOT EXISTS "idx_organizatio_user_id_0dcfbb" ON "organizationmembership" ("user_id");
CREATE TABLE IF NOT EXISTS "task" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "identifier" VARCHAR(64) NOT NULL,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "deadline" TIMESTAMPTZ NOT NULL,
    "is_approved_start" BOOL NOT NULL  DEFAULT False,
    "is_rejected_start" BOOL NOT NULL  DEFAULT False,
    "is_approved_completed" BOOL NOT NULL  DEFAULT False,
    "is_rejected_completed" BOOL NOT NULL  DEFAULT False,
    "is_rewards_claimed" BOOL NOT NULL  DEFAULT False,
    "creation_date" TIMESTAMPTZ NOT NULL,
    "group_id" INT NOT NULL REFERENCES "group" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_task_identif_2964f3" ON "task" ("identifier");
CREATE INDEX IF NOT EXISTS "idx_task_group_i_4b4b90" ON "task" ("group_id");
CREATE TABLE IF NOT EXISTS "taskaction" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "is_submission" BOOL NOT NULL  DEFAULT False,
    "is_review" BOOL NOT NULL  DEFAULT False,
    "action_date" TIMESTAMPTZ NOT NULL,
    "author_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "task_id" INT NOT NULL REFERENCES "task" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "taskreward" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "reward" BIGINT NOT NULL,
    "group_member_id" INT NOT NULL REFERENCES "groupmembership" ("id") ON DELETE CASCADE,
    "task_id" INT NOT NULL REFERENCES "task" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
