"""Tests for episode parsing functions."""
from download import parse_episode_info, get_episode_numbers


class TestParseEpisodeInfo:
    """Tests for parse_episode_info function."""

    def test_standard_format(self):
        assert parse_episode_info("S01E01 One") == (1, 1)
        assert parse_episode_info("S02E15 Ten Green Bottles") == (2, 15)
        assert parse_episode_info("S10E99 Some Title") == (10, 99)

    def test_lowercase_format(self):
        assert parse_episode_info("s01e01 One") == (1, 1)
        assert parse_episode_info("s02e15 Ten Green Bottles") == (2, 15)

    def test_mixed_case_format(self):
        assert parse_episode_info("S01e01 One") == (1, 1)
        assert parse_episode_info("s02E15 Ten Green Bottles") == (2, 15)

    def test_embedded_in_title(self):
        assert parse_episode_info("One | Full Episode - S01E01 | Numberblocks") == (1, 1)
        assert parse_episode_info("The Third Button - Full Episode | S08E01 | Numberblocks") == (8, 1)

    def test_no_episode_info(self):
        assert parse_episode_info("One") == (None, None)
        assert parse_episode_info("Random Title") == (None, None)
        assert parse_episode_info("") == (None, None)

    def test_edge_cases(self):
        assert parse_episode_info("S00E01 Special") == (0, 1)
        assert parse_episode_info("S1E1") == (1, 1)
        assert parse_episode_info("S99E99") == (99, 99)


class TestGetEpisodeNumbers:
    """Tests for get_episode_numbers function."""

    def test_from_config_fields(self):
        ep = {"title": "Custom Title", "id": "abc123", "season": 1, "episode": 5}
        assert get_episode_numbers(ep) == (1, 5)

    def test_from_config_fields_zero_season(self):
        ep = {"title": "Special Episode", "id": "abc123", "season": 0, "episode": 1}
        assert get_episode_numbers(ep) == (0, 1)

    def test_from_title_parsing(self):
        ep = {"title": "S02E10 The Three Threes", "id": "abc123"}
        assert get_episode_numbers(ep) == (2, 10)

    def test_config_fields_take_precedence(self):
        ep = {"title": "S05E10 Wrong", "id": "abc123", "season": 1, "episode": 1}
        assert get_episode_numbers(ep) == (1, 1)

    def test_missing_title(self):
        ep = {"id": "abc123", "season": 1, "episode": 1}
        assert get_episode_numbers(ep) == (1, 1)

    def test_no_info_available(self):
        ep = {"title": "Random Title", "id": "abc123"}
        assert get_episode_numbers(ep) == (None, None)

    def test_empty_episode(self):
        ep = {}
        assert get_episode_numbers(ep) == (None, None)
