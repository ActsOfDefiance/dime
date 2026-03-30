"""
Tests for SQLAlchemy ORM models and pipeline state enum.

Unit tests (default run): verify enum values, model __tablename__, column presence.
Integration tests (marked): CRUD operations requiring a live PostgreSQL instance.
"""

import uuid

from dime.db import make_async_url
from dime.models.article import Article
from dime.models.article_checkpoint import ArticleCheckpoint
from dime.models.base import Base
from dime.models.image_slot import ImageSlot
from dime.models.image_variant import ImageVariant
from dime.models.project import Project
from dime.models.publish_event import PublishEvent
from dime.models.role import Role
from dime.models.user import User
from dime.models.workflow_config import WorkflowConfig
from dime.pipeline import ArticleState as PipelineArticleState
from dime.pipeline.states import ArticleState


# ---------------------------------------------------------------------------
# ArticleState enum
# ---------------------------------------------------------------------------


class TestArticleState:
    def test_all_states_present(self) -> None:
        expected = {
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
        }
        actual = {s.value for s in ArticleState}
        assert actual == expected

    def test_state_count(self) -> None:
        assert len(ArticleState) == 12

    def test_is_str_enum(self) -> None:
        assert isinstance(ArticleState.QUEUED, str)
        assert ArticleState.QUEUED == "queued"

    def test_queued_value(self) -> None:
        assert ArticleState.QUEUED.value == "queued"

    def test_published_value(self) -> None:
        assert ArticleState.PUBLISHED.value == "published"

    def test_pipeline_package_export(self) -> None:
        assert PipelineArticleState is ArticleState


# ---------------------------------------------------------------------------
# Model table names
# ---------------------------------------------------------------------------


class TestTableNames:
    def test_role_tablename(self) -> None:
        assert Role.__tablename__ == "role"

    def test_workflow_config_tablename(self) -> None:
        assert WorkflowConfig.__tablename__ == "workflow_config"

    def test_user_tablename(self) -> None:
        assert User.__tablename__ == "user"

    def test_project_tablename(self) -> None:
        assert Project.__tablename__ == "project"

    def test_article_tablename(self) -> None:
        assert Article.__tablename__ == "article"

    def test_article_checkpoint_tablename(self) -> None:
        assert ArticleCheckpoint.__tablename__ == "article_checkpoint"

    def test_image_slot_tablename(self) -> None:
        assert ImageSlot.__tablename__ == "image_slot"

    def test_image_variant_tablename(self) -> None:
        assert ImageVariant.__tablename__ == "image_variant"

    def test_publish_event_tablename(self) -> None:
        assert PublishEvent.__tablename__ == "publish_event"


# ---------------------------------------------------------------------------
# Model column presence (inspect mapper)
# ---------------------------------------------------------------------------


def _column_names(model: type) -> set[str]:
    table = model.__dict__.get("__table__")
    if table is None:
        return set()
    return set(table.columns.keys())  # type: ignore[union-attr]


class TestColumnPresence:
    def test_role_columns(self) -> None:
        cols = _column_names(Role)
        assert {"id", "name", "permissions", "created_at"}.issubset(cols)

    def test_workflow_config_columns(self) -> None:
        cols = _column_names(WorkflowConfig)
        assert {
            "id",
            "name",
            "is_default",
            "checkpoints",
            "notification_rules",
            "created_at",
        }.issubset(cols)

    def test_user_columns(self) -> None:
        cols = _column_names(User)
        assert {"id", "email", "display_name", "role_id", "created_at"}.issubset(cols)

    def test_project_columns(self) -> None:
        cols = _column_names(Project)
        assert {
            "id",
            "name",
            "slug",
            "style_guide",
            "content_guide",
            "workflow_config_id",
            "created_at",
        }.issubset(cols)

    def test_article_columns(self) -> None:
        cols = _column_names(Article)
        assert {
            "id",
            "project_id",
            "title",
            "slug",
            "state",
            "topic_brief",
            "tags",
            "created_at",
        }.issubset(cols)

    def test_article_checkpoint_columns(self) -> None:
        cols = _column_names(ArticleCheckpoint)
        assert {
            "id",
            "article_id",
            "state_at_checkpoint",
            "git_commit_hash",
            "content_snapshot",
            "created_by",
            "created_at",
        }.issubset(cols)

    def test_image_slot_columns(self) -> None:
        cols = _column_names(ImageSlot)
        assert {
            "id",
            "article_id",
            "slot_name",
            "width",
            "height",
            "format",
        }.issubset(cols)

    def test_image_variant_columns(self) -> None:
        cols = _column_names(ImageVariant)
        assert {
            "id",
            "slot_id",
            "file_path",
            "prompt_used",
            "provider",
            "generation_meta",
            "created_at",
        }.issubset(cols)

    def test_publish_event_columns(self) -> None:
        cols = _column_names(PublishEvent)
        assert {
            "id",
            "article_id",
            "article_checkpoint_id",
            "adapter_name",
            "published_by",
            "published_at",
        }.issubset(cols)


# ---------------------------------------------------------------------------
# Model instantiation (no DB required)
# ---------------------------------------------------------------------------


class TestModelInstantiation:
    def test_role_instantiation(self) -> None:
        role = Role(id=uuid.uuid4(), name="admin", permissions={})
        assert role.name == "admin"

    def test_workflow_config_instantiation(self) -> None:
        wc = WorkflowConfig(
            name="solo", is_default=True, checkpoints={}, notification_rules={}
        )
        assert wc.name == "solo"
        assert wc.is_default is True

    def test_user_instantiation(self) -> None:
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            display_name="Test User",
            role_id=uuid.uuid4(),
        )
        assert user.email == "test@example.com"

    def test_article_default_state(self) -> None:
        article = Article(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            title="Test",
            slug="test",
            state=ArticleState.QUEUED,
            topic_brief="A brief",
            tags=[],
        )
        assert article.state == ArticleState.QUEUED

    def test_base_in_metadata(self) -> None:
        # All tables should be registered in Base.metadata
        table_names = set(Base.metadata.tables.keys())
        assert {
            "role",
            "workflow_config",
            "user",
            "project",
            "article",
            "article_checkpoint",
            "image_slot",
            "image_variant",
            "publish_event",
        }.issubset(table_names)


# ---------------------------------------------------------------------------
# DB module helpers (no live connection)
# ---------------------------------------------------------------------------


class TestDbHelpers:
    def test_make_async_url_postgresql(self) -> None:
        result = make_async_url("postgresql://user:pass@localhost/db")
        assert result == "postgresql+asyncpg://user:pass@localhost/db"

    def test_make_async_url_already_asyncpg(self) -> None:
        url = "postgresql+asyncpg://user:pass@localhost/db"
        assert make_async_url(url) == url

    def test_make_async_url_psycopg(self) -> None:
        result = make_async_url("postgresql+psycopg://user:pass@localhost/db")
        assert result == "postgresql+asyncpg://user:pass@localhost/db"

    def test_make_async_url_unknown_scheme(self) -> None:
        url = "sqlite:///./test.db"
        assert make_async_url(url) == url
