import enum


class ArticleState(str, enum.Enum):
    QUEUED = "queued"
    RESEARCHING = "researching"
    RESEARCH_REVIEW = "research_review"
    WRITING = "writing"
    DRAFT_REVIEW = "draft_review"
    ART_BRIEFING = "art_briefing"
    ART_REVIEW = "art_review"
    ART_GENERATING = "art_generating"
    FINAL_REVIEW = "final_review"
    APPROVED = "approved"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"
