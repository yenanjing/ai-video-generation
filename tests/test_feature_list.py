"""Tests for feature list management."""

import pytest
import tempfile
from pathlib import Path
from agent_harness.state.feature_list import FeatureList, Feature, FeatureStatus


def test_feature_list_creation():
    """Test creating a feature list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_file = Path(tmpdir) / "features.json"
        fl = FeatureList(feature_file)

        assert feature_file.exists()
        assert fl.get_all_features() == []


def test_add_and_get_feature():
    """Test adding and retrieving features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_file = Path(tmpdir) / "features.json"
        fl = FeatureList(feature_file)

        feature = Feature(
            id="F001",
            name="Test Feature",
            description="A test feature",
            acceptance_criteria=["Works correctly"]
        )

        fl.add_feature(feature)
        retrieved = fl.get_feature("F001")

        assert retrieved is not None
        assert retrieved.id == "F001"
        assert retrieved.name == "Test Feature"


def test_update_feature_status():
    """Test updating feature status."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_file = Path(tmpdir) / "features.json"
        fl = FeatureList(feature_file)

        feature = Feature(id="F001", name="Test", description="Test")
        fl.add_feature(feature)

        fl.update_feature_status("F001", FeatureStatus.IN_PROGRESS, notes="Working on it")

        updated = fl.get_feature("F001")
        assert updated.status == FeatureStatus.IN_PROGRESS
        assert updated.notes == "Working on it"


def test_get_next_pending_feature():
    """Test getting next pending feature."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_file = Path(tmpdir) / "features.json"
        fl = FeatureList(feature_file)

        fl.add_feature(Feature(id="F001", name="First", description="First"))
        fl.add_feature(Feature(id="F002", name="Second", description="Second"))

        fl.update_feature_status("F001", FeatureStatus.COMPLETED)

        next_feature = fl.get_next_pending_feature()
        assert next_feature is not None
        assert next_feature.id == "F002"


def test_feature_summary():
    """Test feature summary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_file = Path(tmpdir) / "features.json"
        fl = FeatureList(feature_file)

        fl.add_feature(Feature(id="F001", name="First", description="First"))
        fl.add_feature(Feature(id="F002", name="Second", description="Second"))
        fl.add_feature(Feature(id="F003", name="Third", description="Third"))

        fl.update_feature_status("F001", FeatureStatus.COMPLETED)
        fl.update_feature_status("F002", FeatureStatus.IN_PROGRESS)

        summary = fl.get_summary()
        assert summary["total"] == 3
        assert summary["completed"] == 1
        assert summary["in_progress"] == 1
        assert summary["pending"] == 1
