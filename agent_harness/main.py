"""Main entry point for the agent harness."""

import sys
import argparse
from pathlib import Path
from .config import Config
from .state.progress_tracker import ProgressTracker
from .state.feature_list import FeatureList, Feature, FeatureStatus
from .agents.initializer_agent import InitializerAgent
from .agents.coding_agent import CodingAgent


def init_command():
    """Initialize the environment."""
    print("Initializing environment...")
    Config.validate()
    Config.ensure_workspace()

    # Run initializer agent
    agent = InitializerAgent()
    print(f"Running {agent.name} agent...")
    result = agent.run(max_iterations=20)

    print(f"\nInitializer completed:")
    print(f"  Status: {result['status']}")
    print(f"  Iterations: {result['iterations']}")
    if 'final_message' in result:
        print(f"\nSummary:\n{result['final_message']}")

    # Create initial progress tracker and feature list
    progress_tracker = ProgressTracker(Config.PROGRESS_FILE)
    progress_tracker.log_entry("Environment initialized", session_id="init")

    feature_list = FeatureList(Config.FEATURE_LIST_FILE)
    print("\nEnvironment initialized successfully!")
    print(f"Workspace: {Config.WORKSPACE_DIR}")


def run_command():
    """Run a coding session."""
    print("Starting coding session...")
    Config.validate()

    if not Config.WORKSPACE_DIR.exists():
        print("Error: Workspace not initialized. Run 'init' first.")
        sys.exit(1)

    # Set up state managers
    progress_tracker = ProgressTracker(Config.PROGRESS_FILE)
    feature_list = FeatureList(Config.FEATURE_LIST_FILE)

    # Check for pending features
    next_feature = feature_list.get_next_pending_feature()
    if not next_feature:
        print("No pending features found.")
        summary = feature_list.get_summary()
        print(f"Feature summary: {summary}")
        return

    print(f"Next feature: {next_feature.id} - {next_feature.name}")

    # Create and run coding agent
    agent = CodingAgent(progress_tracker, feature_list)
    print(f"\nRunning {agent.name} agent...")
    result = agent.run(max_iterations=Config.MAX_ITERATIONS)

    print(f"\nCoding session completed:")
    print(f"  Status: {result['status']}")
    print(f"  Iterations: {result['iterations']}")
    if 'final_message' in result:
        print(f"\nSummary:\n{result['final_message']}")


def add_feature_command(args):
    """Add a new feature to the list."""
    Config.ensure_workspace()
    feature_list = FeatureList(Config.FEATURE_LIST_FILE)

    # Generate feature ID
    features = feature_list.get_all_features()
    feature_id = f"F{len(features) + 1:03d}"

    feature = Feature(
        id=feature_id,
        name=args.name,
        description=args.description,
        acceptance_criteria=args.criteria.split(",") if args.criteria else []
    )

    feature_list.add_feature(feature)
    print(f"Added feature: {feature_id} - {feature.name}")


def list_features_command():
    """List all features."""
    feature_list = FeatureList(Config.FEATURE_LIST_FILE)
    features = feature_list.get_all_features()
    summary = feature_list.get_summary()

    print(f"\nFeature Summary: {summary}\n")

    for feature in features:
        status_icon = {
            FeatureStatus.PENDING: "⏳",
            FeatureStatus.IN_PROGRESS: "🔄",
            FeatureStatus.COMPLETED: "✅",
            FeatureStatus.FAILED: "❌"
        }.get(feature.status, "❓")

        print(f"{status_icon} [{feature.status.value.upper()}] {feature.id}: {feature.name}")
        print(f"   {feature.description}")
        if feature.notes:
            print(f"   Notes: {feature.notes}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Agent Harness")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init command
    subparsers.add_parser("init", help="Initialize the environment")

    # Run command
    subparsers.add_parser("run", help="Run a coding session")

    # Add feature command
    add_parser = subparsers.add_parser("add-feature", help="Add a new feature")
    add_parser.add_argument("name", help="Feature name")
    add_parser.add_argument("description", help="Feature description")
    add_parser.add_argument("--criteria", help="Acceptance criteria (comma-separated)")

    # List features command
    subparsers.add_parser("list-features", help="List all features")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "init":
            init_command()
        elif args.command == "run":
            run_command()
        elif args.command == "add-feature":
            add_feature_command(args)
        elif args.command == "list-features":
            list_features_command()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
