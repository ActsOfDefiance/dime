from __future__ import annotations

from dime.pipeline.states import ArticleState

# All valid (from_state, to_state) transitions in the pipeline.
VALID_TRANSITIONS: frozenset[tuple[ArticleState, ArticleState]] = frozenset(
    {
        # Worker path: start triggers research
        (ArticleState.QUEUED, ArticleState.RESEARCHING),
        # Worker completes research
        (ArticleState.RESEARCHING, ArticleState.RESEARCH_REVIEW),
        # Human checkpoint: approve or reject back to researching
        (ArticleState.RESEARCH_REVIEW, ArticleState.WRITING),
        (ArticleState.RESEARCH_REVIEW, ArticleState.RESEARCHING),
        # Worker completes writing
        (ArticleState.WRITING, ArticleState.DRAFT_REVIEW),
        # Human checkpoint: approve or reject back to writing
        (ArticleState.DRAFT_REVIEW, ArticleState.ART_BRIEFING),
        (ArticleState.DRAFT_REVIEW, ArticleState.WRITING),
        # Worker completes art briefing
        (ArticleState.ART_BRIEFING, ArticleState.ART_REVIEW),
        # Human checkpoint: approve or reject back to art briefing
        (ArticleState.ART_REVIEW, ArticleState.ART_GENERATING),
        (ArticleState.ART_REVIEW, ArticleState.ART_BRIEFING),
        # Human approves art generation
        (ArticleState.ART_GENERATING, ArticleState.FINAL_REVIEW),
        # Human checkpoint: approve or reject back to draft review
        (ArticleState.FINAL_REVIEW, ArticleState.APPROVED),
        (ArticleState.FINAL_REVIEW, ArticleState.DRAFT_REVIEW),
        # Publish action
        (ArticleState.APPROVED, ArticleState.PUBLISHING),
        # Worker completes publishing
        (ArticleState.PUBLISHING, ArticleState.PUBLISHED),
        # Re-entry after publish
        (ArticleState.PUBLISHED, ArticleState.DRAFT_REVIEW),
        (ArticleState.PUBLISHED, ArticleState.APPROVED),
    }
)

# States that require a worker task to be dispatched on entry.
WORKER_TASKS: dict[ArticleState, str] = {
    ArticleState.RESEARCHING: "research",
    ArticleState.WRITING: "write",
    ArticleState.ART_BRIEFING: "art_brief",
    ArticleState.PUBLISHING: "publish",
}

# Valid next state when the human approves at a review checkpoint.
APPROVE_TRANSITIONS: dict[ArticleState, ArticleState] = {
    ArticleState.RESEARCH_REVIEW: ArticleState.WRITING,
    ArticleState.DRAFT_REVIEW: ArticleState.ART_BRIEFING,
    ArticleState.ART_REVIEW: ArticleState.ART_GENERATING,
    ArticleState.ART_GENERATING: ArticleState.FINAL_REVIEW,
    ArticleState.FINAL_REVIEW: ArticleState.APPROVED,
}


def is_valid_transition(from_state: ArticleState, to_state: ArticleState) -> bool:
    """Return True if the transition from_state → to_state is permitted."""
    return (from_state, to_state) in VALID_TRANSITIONS


def get_worker_task(state: ArticleState) -> str | None:
    """Return the broker task name to dispatch when entering *state*, or None."""
    return WORKER_TASKS.get(state)
