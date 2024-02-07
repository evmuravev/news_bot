"""create_main_tables

Revision ID: b19effb1e94f
Revises:
Create Date: 2023-04-24 21:18:41.180889

"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'b19effb1e94f'
down_revision = None
branch_labels = None
depends_on = None


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW._updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "_created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "_updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, nullable=False, index=True, unique=True),
        sa.Column("first_name", sa.Text, nullable=True),
        sa.Column("last_name", sa.Text, nullable=True),
        sa.Column("username", sa.Text, nullable=True),
        sa.Column("language_code", sa.Text, nullable=True),
        sa.Column("is_bot", sa.Boolean(), nullable=True),
        sa.Column("link", sa.Text, nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), nullable=True),
        sa.Column("num_of_complains", sa.Integer, default=0),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_news_table() -> None:
    op.create_table(
        "news",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("text", sa.Text, nullable=True),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("video", sa.Text, nullable=True),
        sa.Column("author", sa.Text, nullable=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("message_id", sa.Text, index=True, nullable=True),
        sa.Column("status", sa.Text, default='new', index=True),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_news_modtime
            BEFORE UPDATE
            ON news
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_news_votes_table() -> None:
    op.create_table(
        "news_votes",
        sa.Column("news_id", sa.BigInteger, sa.ForeignKey("news.id", ondelete="CASCADE"), index=True,),
        sa.Column("user_id", sa.BigInteger, index=True, nullable=False),
        sa.Column("pros", sa.BigInteger, nullable=True),
        sa.Column("cons", sa.BigInteger, nullable=True),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_news_votes_modtime
            BEFORE UPDATE
            ON news_votes
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_news_table()
    create_news_votes_table()


def downgrade() -> None:
    op.drop_table("news_votes")
    op.drop_table("news")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
