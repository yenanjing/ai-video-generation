"""Feature list management using JSON for structured requirements."""

import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class FeatureStatus(str, Enum):
    """Status of a feature."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Feature(BaseModel):
    """A feature to be implemented."""
    id: str
    name: str
    description: str
    status: FeatureStatus = FeatureStatus.PENDING
    acceptance_criteria: List[str] = []
    notes: Optional[str] = None
    commit_hash: Optional[str] = None


class FeatureList:
    """Manages the feature list JSON file."""

    def __init__(self, feature_file: Path):
        self.feature_file = feature_file
        self._ensure_file()

    def _ensure_file(self):
        """Ensure feature file exists with initial structure."""
        if not self.feature_file.exists():
            self.feature_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {
                "features": [],
                "metadata": {
                    "created_at": None,
                    "last_updated": None
                }
            }
            self._save(initial_data)

    def _load(self) -> dict:
        """Load feature list from file."""
        with open(self.feature_file, "r") as f:
            return json.load(f)

    def _save(self, data: dict):
        """Save feature list to file."""
        with open(self.feature_file, "w") as f:
            json.dump(data, f, indent=2)

    def add_feature(self, feature: Feature):
        """Add a new feature."""
        data = self._load()
        data["features"].append(feature.model_dump())
        self._save(data)

    def get_all_features(self) -> List[Feature]:
        """Get all features."""
        data = self._load()
        return [Feature(**f) for f in data["features"]]

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Get a specific feature by ID."""
        features = self.get_all_features()
        for feature in features:
            if feature.id == feature_id:
                return feature
        return None

    def get_next_pending_feature(self) -> Optional[Feature]:
        """Get the next pending feature."""
        features = self.get_all_features()
        for feature in features:
            if feature.status == FeatureStatus.PENDING:
                return feature
        return None

    def update_feature_status(self, feature_id: str, status: FeatureStatus,
                            notes: Optional[str] = None,
                            commit_hash: Optional[str] = None):
        """Update feature status."""
        data = self._load()
        for feature in data["features"]:
            if feature["id"] == feature_id:
                feature["status"] = status.value
                if notes:
                    feature["notes"] = notes
                if commit_hash:
                    feature["commit_hash"] = commit_hash
                break
        self._save(data)

    def get_summary(self) -> dict:
        """Get a summary of feature statuses."""
        features = self.get_all_features()
        return {
            "total": len(features),
            "pending": sum(1 for f in features if f.status == FeatureStatus.PENDING),
            "in_progress": sum(1 for f in features if f.status == FeatureStatus.IN_PROGRESS),
            "completed": sum(1 for f in features if f.status == FeatureStatus.COMPLETED),
            "failed": sum(1 for f in features if f.status == FeatureStatus.FAILED),
        }

    def clear_all(self):
        """Clear all features."""
        data = {"features": [], "metadata": {}}
        self._save(data)
