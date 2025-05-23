# Comprehensive Fix for Scene Generation Failures

## Root Cause Analysis

After analyzing the broken output and comparing it to working runs, I've identified the exact bugs:

### **BUG #1: LLM Caching/Repetition Issue**
**Location**: LLM responses are being cached or the LLM is returning identical content
**Evidence**: Same exact scenes despite different prompts
**Fix**: Add uniqueness validation and retry logic

### **BUG #2: Story Outline Not Being Used Properly**
**Location**: `consolidated_playwright.py:_construct_scene_prompt()` line 268
**Evidence**: `current_scene_outline = current_act["key_events"][requirements.scene_number - 1]` may be returning empty or identical content
**Fix**: Ensure story outline has proper distinct key_events for each scene

### **BUG #3: Generation Type Differentiation Not Working**
**Location**: `comprehensive_example.py:generate_act_scenes()` lines 418-470
**Evidence**: All generation types produce identical output
**Fix**: Implement actual different generation pathways

### **BUG #4: Memory/Previous Scene Context Not Applied**
**Location**: Scene generation pipeline
**Evidence**: No progression between scenes
**Fix**: Ensure previous scene content actually influences next scene

## Specific Fixes Required

### Fix 1: Add Scene Uniqueness Validation
```python
def validate_scene_uniqueness(self, new_scene: str, previous_scenes: List[str]) -> bool:
    """Validate that a scene is unique compared to previous scenes."""
    if not previous_scenes:
        return True
    
    # Check for exact duplicates
    for prev_scene in previous_scenes:
        if new_scene.strip() == prev_scene.strip():
            return False
    
    # Check for high similarity (>80% identical)
    from difflib import SequenceMatcher
    for prev_scene in previous_scenes:
        similarity = SequenceMatcher(None, new_scene, prev_scene).ratio()
        if similarity > 0.8:
            return False
    
    return True
```

### Fix 2: Enhance Scene Prompt Specificity
```python
def _construct_detailed_scene_prompt(self, requirements, previous_scenes):
    """Create highly specific prompts to ensure unique scenes."""
    
    # Get specific story beat for this scene
    current_act = self.story_outline.get_act_outline(requirements.act_number)
    scene_event = current_act["key_events"][requirements.scene_number - 1]
    
    # Create scene-specific details
    scene_specifics = {
        1: {"focus": "introduction and setup", "mood": "establishing"},
        2: {"focus": "first major development", "mood": "building tension"},
        3: {"focus": "complication or revelation", "mood": "dramatic"},
        4: {"focus": "crisis or conflict peak", "mood": "intense"},
        5: {"focus": "resolution or transition", "mood": "conclusive"}
    }
    
    specific_focus = scene_specifics[requirements.scene_number]
    
    prompt = f"""
CRITICAL SCENE REQUIREMENTS:
- This is Scene {requirements.scene_number} of Act {requirements.act_number}
- Specific Event: {scene_event}
- Scene Focus: {specific_focus['focus']}
- Required Mood: {specific_focus['mood']}
- MUST be completely different from previous scenes
- MUST advance the plot significantly
- MUST be 2000-4000 characters long

PREVIOUS SCENES SUMMARY (DO NOT REPEAT):
{self._summarize_previous_scenes(previous_scenes)}

UNIQUE ELEMENTS REQUIRED FOR THIS SCENE:
- New dialogue that hasn't appeared before
- Different character interactions
- Progression from previous events
- New plot developments
- Distinct emotional beats

Generate a completely unique scene that advances the story.
"""
    return prompt
```

### Fix 3: Implement Generation Type Differentiation
```python
def generate_scene_with_type(self, requirements, generation_type, previous_scene=None):
    """Generate scene with specific type-based modifications."""
    
    base_prompt = self._construct_detailed_scene_prompt(requirements, previous_scene)
    
    if generation_type == "collaborative":
        # Use two different LLMs and merge responses
        response1 = self.get_llm("openai").invoke(base_prompt + "\nFocus on dialogue and character interaction.")
        response2 = self.get_llm("anthropic").invoke(base_prompt + "\nFocus on narrative and scene description.")
        return self._merge_collaborative_responses(response1, response2)
        
    elif generation_type == "character_focused":
        # Focus on specific character development
        character_prompt = base_prompt + f"\nFOCUS HEAVILY on developing {requirements.characters[0]} character arc and internal journey."
        return self.get_llm().invoke(character_prompt)
        
    elif generation_type == "memory_enhanced":
        # Use extensive memory context
        memory_context = self._get_detailed_memory_context(requirements.act_number, requirements.scene_number)
        enhanced_prompt = base_prompt + f"\nMEMORY CONTEXT TO INTEGRATE:\n{memory_context}"
        return self.get_llm().invoke(enhanced_prompt)
        
    elif generation_type == "iterative_refinement":
        # Generate and refine multiple times
        initial = self.get_llm().invoke(base_prompt)
        refined = self.get_llm().invoke(f"Improve this scene:\n{initial.content}\n\nMake it more detailed, dramatic, and engaging.")
        return refined
        
    else:  # basic
        return self.get_llm().invoke(base_prompt)
```

### Fix 4: Add Scene Retry Logic with Uniqueness Check
```python
def generate_unique_scene(self, requirements, previous_scenes, max_retries=5):
    """Generate a scene with guaranteed uniqueness."""
    
    for attempt in range(max_retries):
        # Generate scene
        scene_result = self.generate_scene_with_type(
            requirements, 
            requirements.generation_type,
            previous_scenes
        )
        
        scene_content = scene_result.content if hasattr(scene_result, 'content') else str(scene_result)
        
        # Validate uniqueness
        if self.validate_scene_uniqueness(scene_content, [s["scene"] for s in previous_scenes]):
            return {
                "scene": scene_content,
                "attempt_number": attempt + 1,
                "generation_type": requirements.generation_type
            }
        
        logger.warning(f"Scene attempt {attempt + 1} was too similar to previous scenes, retrying...")
        
        # Add more specific uniqueness requirements for retry
        requirements.unique_elements = [
            "Different setting details",
            "New character interactions", 
            "Different emotional tone",
            f"Focus on aspect not covered in previous {len(previous_scenes)} scenes"
        ]
    
    raise ValueError(f"Could not generate unique scene after {max_retries} attempts")
```

### Fix 5: Enhanced Story Outline Creation
```python
def create_detailed_story_outline(self, theme, requirements):
    """Create story outline with specific scene beats."""
    
    outline_prompt = f"""
Create a detailed 3-act story outline for "{requirements['title']}" with exactly 15 distinct scenes.

REQUIREMENTS:
- Theme: {theme}
- Setting: {requirements['setting']}
- Style: {requirements['style']}

For each act, provide 5 completely different scene descriptions that advance the plot progressively.

FORMAT REQUIRED:
Act 1: [Description]
Scene 1: [Specific event/situation - establishment]
Scene 2: [Different specific event - first development]  
Scene 3: [Different specific event - complication]
Scene 4: [Different specific event - crisis]
Scene 5: [Different specific event - act conclusion]

Act 2: [Description]
Scene 1: [Specific event - new act beginning]
Scene 2: [Different specific event - development]
Scene 3: [Different specific event - midpoint crisis]
Scene 4: [Different specific event - major complication]
Scene 5: [Different specific event - act climax]

Act 3: [Description]
Scene 1: [Specific event - final act opening]
Scene 2: [Different specific event - final development]
Scene 3: [Different specific event - climax building]
Scene 4: [Different specific event - climax]
Scene 5: [Different specific event - resolution]

Each scene must be completely different with unique situations, dialogue, and character interactions.
"""
    
    response = self.get_llm().invoke(outline_prompt)
    return self._parse_detailed_outline(response.content)
```

## Implementation Priority

1. **IMMEDIATE (P0)**: Fix scene uniqueness validation and retry logic
2. **IMMEDIATE (P0)**: Enhance scene prompt specificity 
3. **HIGH (P1)**: Implement generation type differentiation
4. **HIGH (P1)**: Add memory context integration
5. **MEDIUM (P2)**: Enhance story outline creation

## Testing Strategy

1. **Generate 3 scenes**: Verify each is completely different
2. **Check story progression**: Verify plot advances logically
3. **Validate generation types**: Verify each type produces different output
4. **Test memory integration**: Verify previous scenes influence current scene
5. **Check scene length**: Verify scenes are 2000+ characters

This comprehensive fix addresses all identified root causes and should produce proper unique scenes with narrative progression.