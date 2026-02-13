"""Example usage script."""

from agent_harness.state import FeatureList, Feature, FeatureStatus
from agent_harness.config import Config

# Example: Set up features for a video processing project
Config.ensure_workspace()

feature_list = FeatureList(Config.FEATURE_LIST_FILE)

# Add some example features
features = [
    Feature(
        id="F001",
        name="Video Upload",
        description="Implement video file upload functionality",
        acceptance_criteria=[
            "Support MP4, AVI, MOV formats",
            "Max file size 100MB",
            "Progress bar during upload"
        ]
    ),
    Feature(
        id="F002",
        name="Video Transcoding",
        description="Add video transcoding to H.264",
        acceptance_criteria=[
            "Convert to H.264 codec",
            "Maintain aspect ratio",
            "Generate multiple quality levels"
        ]
    ),
    Feature(
        id="F003",
        name="Thumbnail Generation",
        description="Auto-generate video thumbnails",
        acceptance_criteria=[
            "Extract frame at 25% mark",
            "Generate 3 thumbnail sizes",
            "Save as JPEG"
        ]
    ),
    Feature(
        id="F004",
        name="Video Metadata",
        description="Extract and store video metadata",
        acceptance_criteria=[
            "Duration, resolution, codec",
            "Store in database",
            "Display in UI"
        ]
    ),
    Feature(
        id="F005",
        name="Playback Interface",
        description="Build video playback UI",
        acceptance_criteria=[
            "HTML5 video player",
            "Play/pause, seek controls",
            "Volume control"
        ]
    )
]

for feature in features:
    feature_list.add_feature(feature)

print("Added 5 example features for AI video project")
print("\nNext steps:")
print("1. Configure your .env file with ANTHROPIC_API_KEY")
print("2. Run: python -m agent_harness.main init")
print("3. Run: python -m agent_harness.main run")
