# AI Video Agent Workflow - Architecture

## Overview

This system implements a long-running agent workflow based on Anthropic's best practices. It uses a two-agent approach with persistent state management across sessions.

## Core Components

### 1. Agents

#### Initializer Agent
- **Purpose**: One-time environment setup
- **Responsibilities**:
  - Create init.sh script
  - Set up project structure
  - Initialize git repository
  - Create initial configuration
- **Tools**: Bash, File Read/Write

#### Coding Agent
- **Purpose**: Incremental feature development
- **Workflow per session**:
  1. Get bearings (pwd, git log)
  2. Read progress log
  3. Read feature list
  4. Choose ONE pending feature
  5. Start environment (init.sh)
  6. Run tests
  7. Implement feature
  8. Test and commit
  9. Update status and progress
- **Tools**: Bash, File Read/Write, State Management

### 2. State Management

#### Progress Tracker (claude-progress.txt)
- Logs all agent activities
- Session markers for boundaries
- Timestamped entries
- Enables context across sessions

#### Feature List (feature_list.json)
- Structured task tracking
- JSON format prevents corruption
- Status: pending → in_progress → completed/failed
- Includes acceptance criteria and notes

### 3. Tools System

**Base Tool Interface**:
```python
class BaseTool:
    - name: str
    - description: str
    - input_schema: dict
    - execute(**kwargs) -> ToolResult
```

**Available Tools**:
- `bash`: Execute shell commands
- `read_file`: Read file contents
- `write_file`: Write/create files
- `read_progress`: View progress log
- `read_feature_list`: View all features
- `update_feature_status`: Update feature state

### 4. Session Management

**AgentSession**:
- Manages single agent run
- Handles API calls to Claude
- Executes tool calls
- Tracks iteration count
- Returns structured results

**Session Lifecycle**:
```
Start → Initial Message → API Call → Tool Use → API Call → ... → End
```

## Key Design Patterns

### 1. Incremental Progress
- ONE feature per session
- Prevents overreach and premature completion
- Clear success criteria

### 2. State Bridging
- Explicit state files (not just git)
- Progress log for narrative
- Feature list for structure
- init.sh for environment

### 3. Error Recovery
- Git commits as checkpoints
- Tests before and after changes
- Clean state for merging
- Failure tracking in feature list

### 4. Self-Orientation
Every session starts with standard checklist:
1. Verify location (pwd)
2. Review history (git log)
3. Read progress
4. Check feature list
5. Initialize environment
6. Run tests

### 5. Tool-Based Architecture
- Tools are the agent's hands
- Well-defined interfaces
- Composable and extensible
- Type-safe with Pydantic

## Usage Flow

```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ├─── init ───→ Initializer Agent ───→ Setup Complete
       │
       └─── run ────→ Coding Agent ────────→ Feature Complete
                      │
                      ├─→ Read State
                      ├─→ Choose Feature
                      ├─→ Implement
                      ├─→ Test & Commit
                      └─→ Update State
```

## File Structure

```
ai-video/
├── agent_harness/          # Main package
│   ├── agents/            # Agent implementations
│   ├── tools/             # Tool definitions
│   ├── state/             # State management
│   ├── session/           # Session handling
│   ├── config.py          # Configuration
│   └── main.py            # CLI entry point
├── workspace/             # Agent workspace
│   ├── init.sh           # Environment setup
│   ├── claude-progress.txt
│   └── feature_list.json
├── tests/                 # Test suite
└── examples/              # Usage examples
```

## Extension Points

1. **Add New Tools**: Inherit from `BaseTool`
2. **Custom Agents**: Inherit from `BaseAgent`
3. **State Formats**: Implement new state managers
4. **Session Hooks**: Add pre/post session callbacks

## Best Practices

1. **JSON for structure**: Less prone to corruption
2. **Markdown for narrative**: Human-readable progress
3. **Git for checkpoints**: Reliable rollback
4. **Tests for verification**: Catch previous bugs
5. **One task at a time**: Prevent scope creep
