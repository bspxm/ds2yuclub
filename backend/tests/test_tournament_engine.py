import pytest
from app.plugin.module_badminton.tournament.engine import (
    Participant,
    Group,
    Match,
    TournamentConfig,
    RoundType,
    MatchFormat,
)


@pytest.fixture
def sample_participants():
    return [
        Participant(id=i, name=f"Player {i}", seed_rank=i if i <= 4 else None)
        for i in range(1, 9)
    ]


@pytest.fixture
def sample_config():
    return TournamentConfig(
        tournament_type="round_robin",
        match_format=MatchFormat.BEST_OF_THREE_21,
        points_per_game=21,
        group_size=4,
        num_groups=2,
        advance_from_group=2,
        use_seeding=True,
    )


def test_fixture_works(sample_participants, sample_config):
    assert len(sample_participants) == 8
    assert sample_config.tournament_type == "round_robin"
    assert sample_config.points_per_game == 21
