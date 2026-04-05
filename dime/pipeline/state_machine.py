from __future__ import annotations

from dime.pipeline.states import ArticleState


class InvalidTransitionError(Exception):
    """Raised when a requested state transition is not permitted."""

    def __init__(self, from_state: ArticleState, to_state: ArticleState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Invalid transition: {from_state.value} → {to_state.value}")


# States where the pipeline blocks until a human explicitly acts.
CHECKPOINT_STATES: frozenset[ArticleState] = frozenset(
    {
        ArticleState.RESEARCH_REVIEW,
        ArticleState.DRAFT_REVIEW,
        ArticleState.ART_REVIEW,
        ArticleState.FINAL_REVIEW,
    }
)

# States where automated work is running — FAILED is reachable from any of these.
IN_PROGRESS_STATES: frozenset[ArticleState] = frozenset(
    {
        ArticleState.RESEARCHING,
        ArticleState.WRITING,
        ArticleState.ART_BRIEFING,
        ArticleState.ART_GENERATING,
        ArticleState.PUBLISHING,
    }
)

# All valid (from_state, to_state) transitions.
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
        # Failure: any in-progress state can transition to failed
        *((s, ArticleState.FAILED) for s in IN_PROGRESS_STATES),
        # Archive: any non-terminal state can be archived
        *(
            (s, ArticleState.ARCHIVED)
            for s in ArticleState
            if s is not ArticleState.ARCHIVED
        ),
    }
)

# Valid next state when the human approves at a review checkpoint.
APPROVE_TRANSITIONS: dict[ArticleState, ArticleState] = {
    ArticleState.RESEARCH_REVIEW: ArticleState.WRITING,
    ArticleState.DRAFT_REVIEW: ArticleState.ART_BRIEFING,
    ArticleState.ART_REVIEW: ArticleState.ART_GENERATING,
    ArticleState.ART_GENERATING: ArticleState.FINAL_REVIEW,
    ArticleState.FINAL_REVIEW: ArticleState.APPROVED,
}

# Broker task name dispatched when entering a worker state.
WORKER_TASKS: dict[ArticleState, str] = {
    ArticleState.RESEARCHING: "research",
    ArticleState.WRITING: "write",
    ArticleState.ART_BRIEFING: "art_brief",
    ArticleState.ART_GENERATING: "image",
    ArticleState.PUBLISHING: "publish",
}


def is_valid_transition(from_state: ArticleState, to_state: ArticleState) -> bool:
    """Return True if the transition from_state → to_state is permitted."""
    return (from_state, to_state) in VALID_TRANSITIONS


def transition(from_state: ArticleState, to_state: ArticleState) -> None:
    """Validate the transition and raise InvalidTransitionError if not permitted."""
    if not is_valid_transition(from_state, to_state):
        raise InvalidTransitionError(from_state, to_state)


def is_checkpoint(state: ArticleState) -> bool:
    """Return True if state is a human checkpoint gate."""
    return state in CHECKPOINT_STATES


def get_worker_task(state: ArticleState) -> str | None:
    """Return the broker task name to dispatch when entering *state*, or None."""
    return WORKER_TASKS.get(state)
