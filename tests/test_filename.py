"""Tests for filename generation functions."""
from download import sanitize_title, generate_filename


class TestSanitizeTitle:
    """Tests for sanitize_title function."""

    def test_basic_title(self):
        assert sanitize_title("One") == "One"
        assert sanitize_title("The Third Button") == "The_Third_Button"

    def test_special_characters(self):
        assert sanitize_title("One | Full Episode") == "One_Full_Episode"
        assert sanitize_title("Ten's Top Ten!") == "Tens_Top_Ten"
        assert sanitize_title("What's the Difference?") == "Whats_the_Difference"

    def test_emojis(self):
        assert sanitize_title("Once Upon a Time 👑") == "Once_Upon_a_Time"
        assert sanitize_title("Blockzilla 🦖") == "Blockzilla"

    def test_multiple_spaces(self):
        assert sanitize_title("One   Two   Three") == "One_Two_Three"

    def test_leading_trailing_spaces(self):
        assert sanitize_title("  One  ") == "One"

    def test_empty_string(self):
        assert sanitize_title("") == ""

    def test_only_special_chars(self):
        assert sanitize_title("!!!???") == ""


class TestGenerateFilename:
    """Tests for generate_filename function."""

    def test_default_pattern(self):
        config = {}
        result = generate_filename(config, 1, 1, "One")
        assert result == "S01E01_One.mp4"

    def test_custom_pattern(self):
        config = {"naming_pattern": "{season}_{episode}_{title}.mp4"}
        result = generate_filename(config, 2, 10, "The Three Threes")
        assert result == "2_10_The_Three_Threes.mp4"

    def test_removes_sxxexx_prefix(self):
        config = {}
        result = generate_filename(config, 1, 1, "S01E01 One")
        assert result == "S01E01_One.mp4"

    def test_season_episode_formatting(self):
        config = {}
        assert generate_filename(config, 1, 1, "Test") == "S01E01_Test.mp4"
        assert generate_filename(config, 10, 99, "Test") == "S10E99_Test.mp4"

    def test_special_chars_in_title(self):
        config = {}
        result = generate_filename(config, 1, 1, "What's the Difference?")
        assert result == "S01E01_Whats_the_Difference.mp4"

    def test_zero_season(self):
        config = {}
        result = generate_filename(config, 0, 1, "Special Episode")
        assert result == "S00E01_Special_Episode.mp4"
