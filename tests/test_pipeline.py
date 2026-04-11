"""Unit tests for the pipeline state machine and dispatcher.

No database or broker required — pure logic only.
"""

from __future__ import annotations

import pytest

from dime.pipeline.state_machine import (
    APPROVE_TRANSITIONS,
    CHECKPOINT_STATES,
    IN_PROGRESS_STATES,
    WORKER_TASKS,
    InvalidTransitionError,
    get_worker_task,
    is_checkpoint,
    is_valid_transition,
    transition,
)
from dime.pipeline.states import ArticleState


# ---------------------------------------------------------------------------
# InvalidTransitionError
# ---------------------------------------------------------------------------


class TestInvalidTransitionError:
    def test_message(self) -> None:
        err = InvalidTransitionError(ArticleState.QUEUED, ArticleState.PUBLISHED)
        assert "queued" in str(err)
        assert "published" in str(err)

    def test_attributes(self) -> None:
        err = InvalidTransitionError(ArticleState.WRITING, ArticleState.QUEUED)
        assert err.from_state is ArticleState.WRITING
        assert err.to_state is ArticleState.QUEUED

    def test_is_exception(self) -> None:
        assert issubclass(InvalidTransitionError, Exception)


# ---------------------------------------------------------------------------
# CHECKPOINT_STATES
# ---------------------------------------------------------------------------


class TestCheckpointStates:
    def test_contains_review_states(self) -> None:
        expected = {
            ArticleState.RESEARCH_REVIEW,
            ArticleState.DRAFT_REVIEW,
            ArticleState.ART_REVIEW,
            ArticleState.FINAL_REVIEW,
        }
        assert CHECKPOINT_STATES == expected

    def test_is_frozenset(self) -> None:
        assert isinstance(CHECKPOINT_STATES, frozenset)

    def test_non_review_not_in_checkpoints(self) -> None:
        assert ArticleState.RESEARCHING not in CHECKPOINT_STATES
        assert ArticleState.WRITING not in CHECKPOINT_STATES
        assert ArticleState.PUBLISHED not in CHECKPOINT_STATES


# ---------------------------------------------------------------------------
# IN_PROGRESS_STATES
# ---------------------------------------------------------------------------


class TestInProgressStates:
    def test_contains_worker_states(self) -> None:
        expected = {
            ArticleState.RESEARCHING,
            ArticleState.WRITING,
            ArticleState.ART_BRIEFING,
            ArticleState.ART_GENERATING,
            ArticleState.PUBLISHING,
        }
        assert IN_PROGRESS_STATES == expected

    def test_checkpoint_states_not_in_progress(self) -> None:
        for s in CHECKPOINT_STATES:
            assert s not in IN_PROGRESS_STATES


# ---------------------------------------------------------------------------
# is_valid_transition
# ---------------------------------------------------------------------------


class TestIsValidTransition:
    def test_queued_to_researching(self) -> None:
        assert is_valid_transition(ArticleState.QUEUED, ArticleState.RESEARCHING)

    def test_researching_to_research_review(self) -> None:
        assert is_valid_transition(
            ArticleState.RESEARCHING, ArticleState.RESEARCH_REVIEW
        )

    def test_research_review_approve(self) -> None:
        assert is_valid_transition(ArticleState.RESEARCH_REVIEW, ArticleState.WRITING)

    def test_research_review_reject(self) -> None:
        assert is_valid_transition(
            ArticleState.RESEARCH_REVIEW, ArticleState.RESEARCHING
        )

    def test_full_happy_path(self) -> None:
        path = [
            ArticleState.QUEUED,
            ArticleState.RESEARCHING,
            ArticleState.RESEARCH_REVIEW,
            ArticleState.WRITING,
            ArticleState.DRAFT_REVIEW,
            ArticleState.ART_BRIEFING,
            ArticleState.ART_REVIEW,
            ArticleState.ART_GENERATING,
            ArticleState.FINAL_REVIEW,
            ArticleState.APPROVED,
            ArticleState.PUBLISHING,
            ArticleState.PUBLISHED,
        ]
        for from_s, to_s in zip(path, path[1:]):
            assert is_valid_transition(from_s, to_s), (
                f"{from_s} → {to_s} should be valid"
            )

    def test_invalid_skip(self) -> None:
        assert not is_valid_transition(ArticleState.QUEUED, ArticleState.WRITING)

    def test_invalid_backward_skip(self) -> None:
        assert not is_valid_transition(ArticleState.PUBLISHED, ArticleState.QUEUED)

    def test_invalid_self_transition(self) -> None:
        assert not is_valid_transition(ArticleState.QUEUED, ArticleState.QUEUED)


# ---------------------------------------------------------------------------
# FAILED transitions
# ---------------------------------------------------------------------------


class TestFailedTransitions:
    def test_in_progress_to_failed(self) -> None:
        for state in IN_PROGRESS_STATES:
            assert is_valid_transition(state, ArticleState.FAILED), (
                f"{state} → FAILED should be valid"
            )

    def test_checkpoint_states_can_transition_to_failed(self) -> None:
        # All non-terminal states (including checkpoints) can go to FAILED
        for state in CHECKPOINT_STATES:
            assert is_valid_transition(state, ArticleState.FAILED), (
                f"{state} → FAILED should be valid"
            )

    def test_queued_can_transition_to_failed(self) -> None:
        assert is_valid_transition(ArticleState.QUEUED, ArticleState.FAILED)


# ---------------------------------------------------------------------------
# ARCHIVED transitions
# ---------------------------------------------------------------------------


class TestArchivedTransitions:
    def test_archived_reachable_from_most_states(self) -> None:
        for state in ArticleState:
            if state is ArticleState.ARCHIVED:
                continue
            assert is_valid_transition(state, ArticleState.ARCHIVED), (
                f"{state} → ARCHIVED should be valid"
            )

    def test_archived_is_terminal(self) -> None:
        for state in ArticleState:
            assert not is_valid_transition(ArticleState.ARCHIVED, state), (
                f"ARCHIVED → {state} should be invalid (ARCHIVED is terminal)"
            )


# ---------------------------------------------------------------------------
# transition() raises InvalidTransitionError
# ---------------------------------------------------------------------------


class TestTransitionFunction:
    def test_valid_does_not_raise(self) -> None:
        transition(ArticleState.QUEUED, ArticleState.RESEARCHING)  # no exception

    def test_invalid_raises(self) -> None:
        with pytest.raises(InvalidTransitionError) as exc_info:
            transition(ArticleState.QUEUED, ArticleState.PUBLISHED)
        assert exc_info.value.from_state is ArticleState.QUEUED
        assert exc_info.value.to_state is ArticleState.PUBLISHED

    def test_archived_raises_from_archived(self) -> None:
        with pytest.raises(InvalidTransitionError):
            transition(ArticleState.ARCHIVED, ArticleState.QUEUED)


# ---------------------------------------------------------------------------
# is_checkpoint
# ---------------------------------------------------------------------------


class TestIsCheckpoint:
    def test_review_states_are_checkpoints(self) -> None:
        for state in CHECKPOINT_STATES:
            assert is_checkpoint(state)

    def test_non_review_states_are_not_checkpoints(self) -> None:
        for state in ArticleState:
            if state not in CHECKPOINT_STATES:
                assert not is_checkpoint(state)


# ---------------------------------------------------------------------------
# WORKER_TASKS and get_worker_task
# ---------------------------------------------------------------------------


class TestWorkerTasks:
    def test_research_mapped(self) -> None:
        assert WORKER_TASKS[ArticleState.RESEARCHING] == "research"

    def test_writing_mapped(self) -> None:
        assert WORKER_TASKS[ArticleState.WRITING] == "write"

    def test_art_brief_mapped(self) -> None:
        assert WORKER_TASKS[ArticleState.ART_BRIEFING] == "art_brief"

    def test_image_mapped(self) -> None:
        assert WORKER_TASKS[ArticleState.ART_GENERATING] == "image"

    def test_publish_mapped(self) -> None:
        assert WORKER_TASKS[ArticleState.PUBLISHING] == "publish"

    def test_checkpoint_not_mapped(self) -> None:
        for state in CHECKPOINT_STATES:
            assert get_worker_task(state) is None

    def test_get_worker_task_returns_none_for_unmapped(self) -> None:
        assert get_worker_task(ArticleState.QUEUED) is None
        assert get_worker_task(ArticleState.PUBLISHED) is None
        assert get_worker_task(ArticleState.FAILED) is None
        assert get_worker_task(ArticleState.ARCHIVED) is None


# ---------------------------------------------------------------------------
# APPROVE_TRANSITIONS
# ---------------------------------------------------------------------------


class TestApproveTransitions:
    def test_research_review_advances_to_writing(self) -> None:
        assert APPROVE_TRANSITIONS[ArticleState.RESEARCH_REVIEW] is ArticleState.WRITING

    def test_draft_review_advances_to_art_briefing(self) -> None:
        assert (
            APPROVE_TRANSITIONS[ArticleState.DRAFT_REVIEW] is ArticleState.ART_BRIEFING
        )

    def test_art_review_advances_to_art_generating(self) -> None:
        assert (
            APPROVE_TRANSITIONS[ArticleState.ART_REVIEW] is ArticleState.ART_GENERATING
        )

    def test_art_generating_advances_to_final_review(self) -> None:
        assert (
            APPROVE_TRANSITIONS[ArticleState.ART_GENERATING]
            is ArticleState.FINAL_REVIEW
        )

    def test_final_review_advances_to_approved(self) -> None:
        assert APPROVE_TRANSITIONS[ArticleState.FINAL_REVIEW] is ArticleState.APPROVED

    def test_all_approve_targets_are_valid_transitions(self) -> None:
        for from_s, to_s in APPROVE_TRANSITIONS.items():
            assert is_valid_transition(from_s, to_s), (
                f"APPROVE_TRANSITIONS has unmapped entry: {from_s} → {to_s}"
            )
