# Theatrical Advisors Architecture

## Overview

The theatrical advisors system provides specialized AI agents that analyze and provide feedback on various aspects of theatrical productions. This modular architecture allows for focused expertise in different creative domains.

## Architecture

### Core Components

```
thespian/llm/
├── theatrical_advisors.py    # Main advisor implementations (1,363 lines)
├── advisor_utils.py          # Shared utilities and helpers
└── theatrical_memory.py      # Shared memory system
```

### Advisor Types

The system includes 6 specialized advisor types, each with distinct responsibilities:

| Advisor Type | Responsibility | Primary Focus |
|-------------|----------------|---------------|
| **NarrativeAdvisor** | Story structure and plot | Plot coherence, story arcs, pacing |
| **DialogueAdvisor** | Dialogue quality | Character voice, subtext, naturalism |
| **CharacterAdvisor** | Character development | Consistency, depth, growth |
| **ScenicAdvisor** | Visual staging | Blocking, spatial relationships, visuals |
| **PacingAdvisor** | Timing and rhythm | Scene pacing, dramatic timing |
| **ThematicAdvisor** | Thematic consistency | Theme development, symbolism |

### Design Principles

1. **Single Responsibility**: Each advisor focuses on one aspect of production
2. **Modular Design**: Advisors can be used independently or together
3. **Extensibility**: New advisor types can be added easily
4. **Consistency**: All advisors follow the same interface pattern

## File Structure Analysis

### theatrical_advisors.py (1,363 lines)

**Well-organized sections:**
- Lines 1-85: Base classes and types
- Lines 86-221: NarrativeAdvisor
- Lines 222-344: DialogueAdvisor
- Lines 345-466: CharacterAdvisor
- Lines 467-580: ScenicAdvisor
- Lines 581-712: PacingAdvisor
- Lines 713-830: ThematicAdvisor
- Lines 831-1130: NarrativeContinuityAdvisor
- Lines 1131-1363: AdvisorManager

**Why not split further:**
- Each advisor is self-contained (~100-150 lines)
- Clear separation between advisor types
- Shared base classes would create circular dependencies
- Current structure is well-documented
- No code duplication between advisors

## Usage Examples

### Individual Advisor

```python
from thespian.llm.theatrical_advisors import DialogueAdvisor
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory

llm_manager = LLMManager()
memory = TheatricalMemory()

advisor = DialogueAdvisor(
    name="Dialogue Expert",
    llm_manager=llm_manager,
    memory=memory
)

feedback = advisor.analyze(
    content=scene_dialogue,
    context={"act": 1, "scene": 2}
)

print(f"Score: {feedback.score}")
print(f"Feedback: {feedback.feedback}")
print(f"Suggestions: {feedback.suggestions}")
```

### Advisor Manager

```python
from thespian.llm.theatrical_advisors import AdvisorManager

manager = AdvisorManager(
    llm_manager=llm_manager,
    memory=memory
)

# Get feedback from all advisors
all_feedback = manager.get_comprehensive_feedback(
    content=scene_content,
    context=production_context
)

# Or use specific advisors
narrative_feedback = manager.get_advisor_feedback(
    advisor_type="narrative",
    content=scene_content
)
```

## Utilities (advisor_utils.py)

Shared utilities reduce code duplication:

- **extract_key_phrases()**: Extract important phrases for analysis
- **calculate_feedback_score()**: Weighted scoring system
- **prioritize_suggestions()**: Order suggestions by importance
- **format_advisor_response()**: Standardized response formatting
- **validate_content_length()**: Input validation
- **AdvisorMetrics**: Standard metrics tracking

## Maintenance Guidelines

### Adding New Advisor Types

1. Create new class inheriting from `TheatricalAdvisor`
2. Implement `analyze()` method
3. Add to `AdvisorType` enum
4. Register in `AdvisorManager`

Example:
```python
class MotivationAdvisor(TheatricalAdvisor):
    """Advisor for character motivation analysis."""
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        super().__init__(
            name=name,
            expertise=AdvisorType.MOTIVATION,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        # Implementation here
        pass
```

### Code Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Lines of code | 1,363 | 🟡 Large but organized |
| Classes | 11 | 🟢 Well-structured |
| Methods | 33 | 🟢 Reasonable |
| Documentation | Comprehensive | 🟢 Excellent |
| Code duplication | Minimal | 🟢 Good |
| Test coverage | Partial | 🟡 Can improve |

## Future Enhancements

1. **Performance Optimization**
   - Cache advisor responses for similar content
   - Implement parallel advisor execution
   - Add response streaming for long content

2. **Enhanced Analysis**
   - Add ML-based sentiment analysis
   - Implement cross-advisor collaboration
   - Add historical feedback tracking

3. **Testing**
   - Add unit tests for each advisor type
   - Create integration tests for AdvisorManager
   - Add performance benchmarks

4. **Documentation**
   - Add API reference documentation
   - Create tutorial notebooks
   - Add more usage examples

## Conclusion

The theatrical advisors system is well-architected with clear separation of concerns. While the main file is large (1,363 lines), it's well-organized and doesn't require immediate refactoring. The addition of advisor_utils.py provides shared functionality without disrupting the existing structure.

**Recommendation**: Keep current structure, enhance with utilities and tests rather than splitting into multiple files which could create maintenance overhead.
