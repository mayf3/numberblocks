"""Tests for configuration loading and validation."""
import tempfile
from pathlib import Path

import yaml
from download import load_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self):
        config_content = """
series_name: "Test Series"
description: "Test description"
quality: 1080
episodes:
  Season 1:
    - title: "S01E01 Test"
      id: "abc123"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config = load_config(Path(f.name))
        
        assert config['series_name'] == "Test Series"
        assert config['quality'] == 1080
        assert 'Season 1' in config['episodes']
        assert len(config['episodes']['Season 1']) == 1

    def test_load_config_with_subtitles(self):
        config_content = """
series_name: "Test"
subtitles:
  enabled: true
  lang: "en"
  embed: true
episodes:
  Season 1:
    - title: "S01E01 Test"
      id: "abc123"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config = load_config(Path(f.name))
        
        assert config['subtitles']['enabled'] == True
        assert config['subtitles']['lang'] == "en"

    def test_load_config_with_custom_patterns(self):
        config_content = """
series_name: "Test"
naming_pattern: "{season}_{episode}_{title}.mp4"
directory_pattern: "Series_{series_name}"
episodes:
  Season 1:
    - title: "S01E01 Test"
      id: "abc123"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config = load_config(Path(f.name))
        
        assert config['naming_pattern'] == "{season}_{episode}_{title}.mp4"
        assert config['directory_pattern'] == "Series_{series_name}"

    def test_load_actual_numberblocks_config(self):
        config_path = Path(__file__).parent.parent / "config" / "series" / "numberblocks.yaml"
        if config_path.exists():
            config = load_config(config_path)
            assert config['series_name'] == "Numberblocks"
            assert 'episodes' in config
            assert len(config['episodes']) > 0


class TestConfigStructure:
    """Tests for config structure validation."""

    def test_episode_has_required_fields(self):
        config_content = """
series_name: "Test"
episodes:
  Season 1:
    - title: "S01E01 Test"
      id: "abc123"
      season: 1
      episode: 1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config = load_config(Path(f.name))
        
        ep = config['episodes']['Season 1'][0]
        assert 'title' in ep
        assert 'id' in ep
        assert ep['id'] == "abc123"

    def test_multiple_seasons(self):
        config_content = """
series_name: "Test"
episodes:
  Season 1:
    - title: "S01E01 Test"
      id: "abc123"
  Season 2:
    - title: "S02E01 Test"
      id: "def456"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            f.flush()
            config = load_config(Path(f.name))
        
        assert len(config['episodes']) == 2
        assert 'Season 1' in config['episodes']
        assert 'Season 2' in config['episodes']
