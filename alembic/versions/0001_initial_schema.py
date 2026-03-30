"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-03-29 19:20:18.169456

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type first
    articlestate = postgresql.ENUM(
        "queued",
        "researching",
        "research_review",
        "writing",
        "draft_review",
        "art_briefing",
        "art_review",
        "art_generating",
        "final_review",
        "approved",
        "publishing",
        "published",
        name="articlestate",
    )
    articlestate.create(op.get_bind())

    op.create_table(
        "role",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("permissions", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "workflow_config",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("checkpoints", postgresql.JSONB(), nullable=False),
        sa.Column("notification_rules", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "project",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("style_guide", postgresql.JSONB(), nullable=False),
        sa.Column("content_guide", postgresql.JSONB(), nullable=False),
        sa.Column("workflow_config_id", sa.Uuid(), nullable=False),
        sa.Column("default_adapter", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["workflow_config_id"], ["workflow_config.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # article — no current_draft_id FK yet (use_alter — added after article_checkpoint)
    op.create_table(
        "article",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("state", sa.Enum("articlestate", create_type=False), nullable=False),
        sa.Column("topic_brief", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), nullable=True),
        sa.Column("current_draft_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["assigned_to"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_article_project_id_state", "article", ["project_id", "state"])

    op.create_table(
        "article_checkpoint",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("article_id", sa.Uuid(), nullable=False),
        sa.Column(
            "state_at_checkpoint",
            sa.Enum("articlestate", create_type=False),
            nullable=False,
        ),
        sa.Column("git_commit_hash", sa.Text(), nullable=True),
        sa.Column("content_snapshot", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add deferred FK: article.current_draft_id → article_checkpoint.id
    op.create_foreign_key(
        "fk_article_current_draft_id",
        "article",
        "article_checkpoint",
        ["current_draft_id"],
        ["id"],
    )

    # image_variant before image_slot (image_slot.selected_variant_id uses use_alter)
    op.create_table(
        "image_variant",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slot_id", sa.Uuid(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("prompt_used", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("generation_meta", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        # slot_id FK added after image_slot exists
    )

    op.create_table(
        "image_slot",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("article_id", sa.Uuid(), nullable=False),
        sa.Column("slot_name", sa.String(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("format", sa.String(), nullable=False),
        sa.Column("approved_prompt", sa.Text(), nullable=True),
        sa.Column("selected_variant_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"]),
        sa.PrimaryKeyConstraint("id"),
        # selected_variant_id FK added after image_variant exists
    )
    op.create_index("ix_image_slot_article_id", "image_slot", ["article_id"])

    # Add deferred FKs for image circular references
    op.create_foreign_key(
        "fk_image_slot_selected_variant_id",
        "image_slot",
        "image_variant",
        ["selected_variant_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_image_variant_slot_id",
        "image_variant",
        "image_slot",
        ["slot_id"],
        ["id"],
    )

    op.create_table(
        "publish_event",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("article_id", sa.Uuid(), nullable=False),
        sa.Column("article_checkpoint_id", sa.Uuid(), nullable=False),
        sa.Column("adapter_name", sa.Text(), nullable=False),
        sa.Column("adapter_version", sa.Text(), nullable=False),
        sa.Column("target_url", sa.Text(), nullable=True),
        sa.Column("published_by", sa.Uuid(), nullable=False),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["article.id"]),
        sa.ForeignKeyConstraint(["article_checkpoint_id"], ["article_checkpoint.id"]),
        sa.ForeignKeyConstraint(["published_by"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("publish_event")

    op.drop_constraint("fk_image_variant_slot_id", "image_variant", type_="foreignkey")
    op.drop_constraint(
        "fk_image_slot_selected_variant_id", "image_slot", type_="foreignkey"
    )
    op.drop_index("ix_image_slot_article_id", table_name="image_slot")
    op.drop_table("image_slot")
    op.drop_table("image_variant")

    op.drop_constraint("fk_article_current_draft_id", "article", type_="foreignkey")
    op.drop_table("article_checkpoint")
    op.drop_index("ix_article_project_id_state", table_name="article")
    op.drop_table("article")
    op.drop_table("project")
    op.drop_table("user")
    op.drop_table("workflow_config")
    op.drop_table("role")

    sa.Enum(name="articlestate").drop(op.get_bind())
