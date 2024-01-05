from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "organization" DROP COLUMN "type";
        ALTER TABLE "task" ADD "owner_membership_id" INT;
        ALTER TABLE "task" ADD "is_individual" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "task" ALTER COLUMN "group_id" DROP NOT NULL;
        CREATE TABLE IF NOT EXISTS "taskfund" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "amount" BIGINT NOT NULL,
    "is_completed" BOOL NOT NULL  DEFAULT False,
    "complete_date" TIMESTAMPTZ,
    "task_id" INT NOT NULL REFERENCES "task" ("id") ON DELETE CASCADE,
    "user_member_id" INT NOT NULL REFERENCES "organizationmembership" ("id") ON DELETE CASCADE
);
        ALTER TABLE "taskreward" ADD "complete_date" TIMESTAMPTZ;
        ALTER TABLE "taskreward" ADD "is_completed" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "user" ADD "payment_address" VARCHAR(128);
        CREATE TABLE IF NOT EXISTS "userbalance" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "amount" BIGINT NOT NULL,
    "is_claimed" BOOL NOT NULL  DEFAULT False,
    "is_escrowed" BOOL NOT NULL  DEFAULT False,
    "is_error" BOOL NOT NULL  DEFAULT False,
    "claim_error" TEXT,
    "balance_date" TIMESTAMPTZ NOT NULL,
    "claim_date" TIMESTAMPTZ,
    "escrow_task_fund_id" INT REFERENCES "taskfund" ("id") ON DELETE CASCADE,
    "user_member_id" INT NOT NULL REFERENCES "organizationmembership" ("id") ON DELETE CASCADE
);
        CREATE INDEX "idx_task_owner_m_947955" ON "task" ("owner_membership_id");
        ALTER TABLE "task" ADD CONSTRAINT "fk_task_organiza_f7dcc09a" FOREIGN KEY ("owner_membership_id") REFERENCES "organizationmembership" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "task" DROP CONSTRAINT "fk_task_organiza_f7dcc09a";
        DROP INDEX "idx_task_owner_m_947955";
        ALTER TABLE "task" DROP COLUMN "owner_membership_id";
        ALTER TABLE "task" DROP COLUMN "is_individual";
        ALTER TABLE "task" ALTER COLUMN "group_id" SET NOT NULL;
        ALTER TABLE "user" DROP COLUMN "payment_address";
        ALTER TABLE "taskreward" DROP COLUMN "complete_date";
        ALTER TABLE "taskreward" DROP COLUMN "is_completed";
        ALTER TABLE "organization" ADD "type" VARCHAR(16) NOT NULL;
        DROP TABLE IF EXISTS "taskfund";
        DROP TABLE IF EXISTS "userbalance";"""
