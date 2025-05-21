# Thespian: AI-Driven Theatrical Production Framework

An agentic framework for autonomous theatrical creation by AI collectives, enabling the entire lifecycle of theatrical production from script to performance.

## Overview

Thespian is a sophisticated multi-agent system that orchestrates AI agents to create and perform theatrical productions. The framework leverages Large Language Models (LLMs) to power specialized agents that take on traditional theatre roles such as Playwright, Director, Character Actors, Set & Costume Designer, and Stage Manager.

## Key Features

- **Multi-Agent Architecture**: Specialized AI agents working in concert to create theatrical productions
- **Hierarchical-Hybrid Orchestration**: Balancing centralized creative direction with flexible peer-to-peer interactions
- **Integrated Development Environment**: Tools for agent configuration, script development, rehearsal simulation, and performance orchestration
- **Human-in-the-Loop Collaboration**: Active participation and guidance of the creative process
- **Advanced Story Structure System**: Sophisticated narrative structure tools for complex storytelling patterns
- **Enhanced Memory & Character Development**: Rich character tracking and narrative continuity
- **Iterative Refinement**: Multi-pass scene improvement for higher quality output

## Core Components

1. **Playwright Agent**: Generates play concepts, develops plots, creates characters, and crafts dialogue
2. **Director Agent**: Defines artistic vision, guides other agents, and ensures creative coherence
3. **Character Actor Agents**: Embody specific characters and interpret their roles
4. **Set & Costume Design Agent**: Creates textual descriptions of visual elements
5. **Stage Manager Agent**: Coordinates production workflow and performance execution
6. **Advanced Story Structure System**: Manages complex narrative structures beyond the standard 3-act format
7. **Memory Enhancement System**: Tracks character development and narrative continuity
8. **Iterative Refinement System**: Improves scene quality through multiple focused passes

## Quickstart

1. **Install dependencies:**
   ```bash
   git clone https://github.com/yourusername/thespian.git
   cd thespian
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

2. **Configure LLMs:**
   - For Grok: `python add_api_key.py` and follow prompts (API key saved to `.env`).
   - For Ollama: Ensure Ollama is running locally (see docs).

3. **Run an example production:**
   ```bash
   python examples/simple_production.py
   ```

4. **Try advanced features:**
   ```bash
   # Run with the enhanced systems
   python examples/combined_enhancements_example.py
   
   # Try the advanced story structure demo
   python examples/demo_advanced_structure_capabilities.py
   ```

## Architecture Diagram

## How It Works

Thespian orchestrates multiple AI agents (Playwright, Director, Character Actors, etc.) to collaboratively generate and perform theatrical productions. Each agent may use a different LLM model (Ollama or Grok) depending on configuration and agent ID. The LLMManager uses a hash of the agent's ID to consistently assign a model, allowing you to balance local and API-based inference. You can adjust the percentage of agents using each model (see LLM configuration below).


```
+-------------------+
|    Theatre (API)  |
+-------------------+
           |
+-------------------+
|   Production      |
+-------------------+
      |        |
+-----+   +------------------+
| Playwright/Director/Actors |
+-----+   +------------------+
      |        |
+-------------------+
|   LLMManager      |
+-------------------+
      |        |
+-----+   +------------------+
| Ollama  |   Grok (API)     |
+-----+   +------------------+
```

## Enhanced Systems

Thespian includes three major enhancement systems that work together to create more sophisticated, detailed, and coherent theatrical productions:

### 1. Advanced Story Structure System

Enables complex narrative structures beyond the standard three-act format:
- Multiple narrative structure types (linear, non-linear, parallel, nested, etc.)
- Various act structure patterns (3-act, 5-act, hero's journey, etc.)
- Story beat tracking and management
- Plot thread and subplot coordination
- Strategic plot reversals and twists

See [USER_GUIDE_ADVANCED_STRUCTURE.md](USER_GUIDE_ADVANCED_STRUCTURE.md) for detailed usage.

### 2. Memory and Continuity System

Provides sophisticated character and narrative tracking:
- Enhanced character profiles with psychological depth
- Character development arc tracking
- Relationship development history
- Narrative continuity across scenes
- Thematic and plot point tracking

### 3. Iterative Refinement System

Improves scene quality through multiple enhancement passes:
- Multi-pass scene refinement with targeted improvements
- Enhanced prompts for more detailed generation
- Quality analysis and problem identification
- Sensory detail and character psychology enhancements

See [ENHANCEMENTS_MASTER_README.md](ENHANCEMENTS_MASTER_README.md) for comprehensive documentation of all enhancement systems.

## Module Explanations

- **thespian/theatre.py**: Main entry point for creating and running productions.
- **thespian/production.py**: Handles production state, script, design, characters.
- **thespian/performance.py**: Orchestrates performance execution.
- **thespian/llm/**: LLM management, agent personas, dialogue, advisors, memory, quality control, scene structure.
  - **llm/advanced_story_structure.py**: Advanced narrative structure management system
  - **llm/enhanced_memory.py**: Enhanced character and narrative memory tracking
  - **llm/iterative_refinement.py**: Multi-pass scene quality improvement system
- **thespian/ide/**: Interactive tools (performance dashboard, rehearsal sandbox, script editor).
- **thespian/agents.py**: Core agent classes (PlaywrightAgent, DirectorAgent, etc).
- **examples/**: Example scripts for onboarding and demonstration.
- **tests/**: Automated tests for core and integration functionality.



```bash
# Clone the repository
git clone https://github.com/yourusername/thespian.git
cd thespian

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

### LLM Model Selection & Agent Mapping

Thespian supports two LLM backends:
1. **Ollama**: Runs locally (default model: `long-gemma`).
2. **Grok**: Cloud API (default model: `grok-3-beta`, requires API key).

The `LLMManager` assigns models to agents using a hash of the agent's ID and the `ollama_usage_percentage` value (default: 0.5, or 50%). For example, if you want 80% of agents to use Ollama, set:

```toml
ollama_usage_percentage = 0.8
```

in your configuration. This ensures consistent, reproducible agent-to-model mapping.

#### Setting the Grok API Key

```bash
# Run the API key setup script
python add_api_key.py

# Follow the prompts to enter your API key
# The key will be stored in a .env file

# Restart your terminal or run the following to apply changes
source .env
```

## Usage

### Basic Usage

```python
from thespian import Theatre

# Initialize the theatre with a theme
theatre = Theatre(theme="A modern retelling of Romeo and Juliet in a cyberpunk setting")

# Start the production process
production = theatre.create_production()

# Run the performance
performance = production.perform()
```

### Using Advanced Story Structure

```python
from thespian.llm.advanced_story_structure import (
    AdvancedStoryPlanner, 
    NarrativeStructureType,
    ActStructureType
)

# Create a non-linear story with hero's journey structure
story_planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.NON_LINEAR,
    act_structure=ActStructureType.HERO_JOURNEY,
    num_acts=3,
    narrative_complexity="complex"
)

# Define plot threads, subplots, and reversals
# ...

# Use in a production
# ...
```

For comprehensive examples of using the advanced systems, see:
- `examples/advanced_story_structure_demo.py`
- `examples/combined_enhancements_example.py`

## Testing & Troubleshooting

To run the test suite:

```bash
pytest --maxfail=3 --disable-warnings -v
```

- Some integration tests (especially those involving LLM calls) may take 1-2 minutes or more to complete.
- If tests seem stuck, be patient—network/API-based LLMs can be slow.
- To run only a specific test, use:

```bash
pytest -k test_name
```

- If you see warnings but no failures, tests are likely passing. If you interrupt (`Ctrl+C`), rerun to see full results.

## Development

The project uses modern Python tooling:
- `pyproject.toml` for project metadata and dependencies
- `ruff` for linting
- `pytest` for testing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 