"""Prompt templates for scene generation and processing."""

from typing import Dict

SCENE_GENERATION_PROMPT = """Generate a detailed scene for {title} following this outline:

ACT {act_number} CONTEXT:
{act_description}

SCENE {scene_number} REQUIREMENT:
{scene_outline}

TECHNICAL REQUIREMENTS:
- Setting: {setting}
- Characters: {characters}
- Props: {props}
- Lighting: {lighting}
- Sound: {sound}
- Style: {style}
- Period: {period}
- Target Audience: {target_audience}

CONTINUITY REQUIREMENTS:
1. Previous Scene: {previous_scene}
2. Previous Feedback: {previous_feedback}
3. Must advance the plot according to the key event
4. Must maintain character consistency
5. Must include all required technical elements
6. Must create dramatic tension
7. Must set up the next scene's events

{uniqueness_constraint}

{scene_directive}

SCENE STRUCTURE REQUIREMENTS:
1. Length: {min_length}-{max_length} characters
2. Must have a clear beginning, middle, and end
3. Must include detailed stage directions
4. Must have natural, varied dialogue
5. Must create dramatic tension
6. Must include sensory details (sight, sound, smell, etc.)
7. Must have clear character motivations
8. Must include emotional beats
{memory_context}
{narrative_context}

CRITICAL FORMATTING REQUIREMENTS (MUST BE FOLLOWED EXACTLY):
1. Character names MUST be in ALL CAPS followed by a colon (example: LYRA:)
2. Stage directions MUST be in (parentheses) on their own lines
3. Technical cues MUST be in [brackets] on their own lines
4. Dialogue must follow character names immediately after the colon
5. NO markdown formatting whatsoever (no **, *, _, etc.)
6. NO bold, italic, or any special formatting
7. Use only standard ASCII characters and punctuation
8. Every scene MUST include at least 3 stage directions in (parentheses)
9. Every scene MUST include at least 2 technical cues in [brackets]
10. Every character name MUST appear in ALL CAPS throughout the scene
11. Character names can be single words (LYRA) or multiple words (SPECTRAL WOMAN)
12. Each line of dialogue should show character emotion and intention
13. Stage directions should describe physical actions, movements, and emotional states
14. Technical cues should specify lighting, sound, or other technical elements

EXAMPLE OF CORRECT FORMATTING:
LYRA: (walking nervously to the window) I can't shake this feeling that something's watching us.

(She turns suddenly, her eyes wide with concern)

SPECTRAL WOMAN: (appearing from the shadows, voice echoing) Your instincts serve you well, child.

[Dim lighting shifts to create an ethereal atmosphere]

LYRA: (backing away, voice trembling) Who are you? What do you want?

(The room seems to grow colder as the figure approaches)

[Soft, haunting music begins to play]

Format your response EXACTLY as follows:

SCENE CONTENT:
[Your scene content following the format above]

NARRATIVE ANALYSIS:
1. How this scene advances the plot
2. Character development shown
3. Thematic elements explored
4. Technical elements integrated
5. Connection to previous scene
6. Setup for next scene"""

SCENE_DEVELOPMENT_PROMPT = """Develop this scene by enhancing its existing content. The scene is currently {current_length} characters long and needs to be between {min_length} and {max_length} characters.

Current Scene:
{scene_content}

Development Requirements:
1. For each line of dialogue:
   - Add more detailed stage directions showing character emotions and physical reactions
   - Include internal thoughts and motivations
   - Add more specific gestures and movements
   - Show how the character's state affects their delivery

2. For each stage direction:
   - Add more sensory details
   - Include more specific physical actions
   - Show more emotional nuance
   - Connect actions to character motivations

3. For each technical cue:
   - Add more atmospheric details
   - Include more specific lighting changes
   - Add more sound effects
   - Show how technical elements affect the mood

4. For each scene transition:
   - Add more detailed technical cues
   - Show how the environment changes
   - Include more atmospheric elements
   - Connect transitions to the emotional state

Format your response EXACTLY as follows:

SCENE CONTENT:
[Your developed scene content following the same format]

NARRATIVE ANALYSIS:
1. How this scene advances the plot
2. Character development shown
3. Thematic elements explored
4. Technical elements integrated
5. Connection to previous scene
6. Setup for next scene"""

SCENE_IMPROVEMENT_PROMPT = """Improve this scene based on the following feedback:

Current Scene:
{scene_content}

Quality Evaluation:
- Character Consistency: {character_consistency}
- Thematic Coherence: {thematic_coherence}
- Technical Accuracy: {technical_accuracy}
- Dramatic Impact: {dramatic_impact}
- Dialogue Quality: {dialogue_quality}
- Stage Direction Quality: {stage_direction_quality}

Specific Suggestions:
{suggestions}

Requirements:
- Target length: {min_length}-{max_length} characters
- Must maintain continuity with previous scenes
- Must incorporate all technical elements (props, lighting, sound)
- Must develop characters meaningfully
- Must advance the plot and themes
- Must include detailed stage directions
- Must have natural, varied dialogue
- Must create dramatic tension
- Must include sensory details (sight, sound, smell, etc.)
- Must have clear character motivations
- Must include emotional beats
- Must have a clear beginning, middle, and end

Format your response EXACTLY as follows:

SCENE CONTENT:
[Your improved scene content following the same format]

NARRATIVE ANALYSIS:
1. How this scene advances the plot
2. Character development shown
3. Thematic elements explored
4. Technical elements integrated
5. Connection to previous scene
6. Setup for next scene"""

ACT_PLANNING_ADVISOR_PROMPT = """As a {advisor_type} advisor, help plan Act {act_number} of {title}.

CRITICAL FORMAT REQUIREMENTS:
1. You MUST write each section header EXACTLY as shown below, in ALL CAPS
2. You MUST include ALL four sections in this EXACT order:
   - DESCRIPTION
   - KEY EVENTS
   - CHARACTER DEVELOPMENT
   - THEMATIC ELEMENTS
3. You MUST separate each section with a blank line
4. For KEY EVENTS section:
   - You MUST write exactly 5 numbered key events
   - Each event MUST be numbered 1-5 followed by a period and space
   - Each event MUST be a complete sentence ending with a period
   - Each event MUST be at least 20 characters long
   - Each event MUST describe a specific plot point or character action
   - Example format:
     1. The protagonist discovers a mysterious artifact that changes their life.
     2. The antagonist reveals their true intentions to the protagonist.
     3. A key supporting character is introduced and forms an alliance with the protagonist.
     4. The first major conflict occurs between the protagonist and antagonist.
     5. The act concludes with a revelation that changes the protagonist's understanding of their situation.
   - BAD EXAMPLE (do NOT do this):
     1. Introduction.
     2. Conflict.
     3. Resolution.
     4. 
     5. 
   - GOOD EXAMPLE (do this):
     1. The protagonist discovers a mysterious artifact that changes their life.
     2. The antagonist reveals their true intentions to the protagonist.
     3. A key supporting character is introduced and forms an alliance with the protagonist.
     4. The first major conflict occurs between the protagonist and antagonist.
     5. The act concludes with a revelation that changes the protagonist's understanding of their situation.
5. You MUST NOT use any markdown formatting
6. You MUST NOT use any special characters except standard punctuation

Previous acts: {previous_acts}
Previous scenes: {previous_scenes}

Consider:
1. The overall narrative arc
2. Character development opportunities
3. Thematic elements to explore
4. Technical requirements
5. How this act should connect to previous and future acts
6. Pacing and dramatic tension
7. Audience engagement

EXAMPLE RESPONSE:
DESCRIPTION:
This act serves as the catalyst for the story's central conflict, introducing the main characters and their initial motivations. It establishes the world and sets up the dramatic tension that will drive the narrative forward.

KEY EVENTS:
1. The protagonist discovers a mysterious artifact that changes their life.
2. The antagonist reveals their true intentions to the protagonist.
3. A key supporting character is introduced and forms an alliance with the protagonist.
4. The first major conflict occurs between the protagonist and antagonist.
5. The act concludes with a revelation that changes the protagonist's understanding of their situation.

CHARACTER DEVELOPMENT:
The protagonist begins as naive and uncertain, but the events of this act force them to confront their fears and begin their journey of growth. The antagonist's true nature is revealed, showing their complexity and motivation.

THEMATIC ELEMENTS:
This act explores themes of discovery, betrayal, and the beginning of transformation. It sets up the central themes that will be developed throughout the story.

---

CHECKLIST BEFORE YOU SUBMIT:
- [ ] Did you write exactly 5 key events, each at least 20 characters, each a complete sentence?
- [ ] Did you use the correct section headers in ALL CAPS?
- [ ] Did you separate each section with a blank line?
- [ ] Did you avoid markdown and special characters?
- [ ] Did you follow the GOOD EXAMPLE format for key events?

If this is a retry after a failed attempt, here is corrective feedback from the previous attempt:
{corrective_feedback}
"""

ACT_PLANNING_SYNTHESIS_PROMPT = """Synthesize the following advisor suggestions for Act {act_number} into a coherent act outline.

CRITICAL FORMAT REQUIREMENTS:
1. You MUST write each section header EXACTLY as shown below, in ALL CAPS
2. You MUST include ALL four sections in this EXACT order:
   - DESCRIPTION
   - KEY EVENTS
   - CHARACTER DEVELOPMENT
   - THEMATIC ELEMENTS
3. You MUST separate each section with a blank line
4. You MUST write exactly 5 numbered key events (1-5)
5. You MUST NOT use any markdown formatting
6. You MUST NOT use any special characters except standard punctuation

Advisor Suggestions:
{advisor_suggestions}

Previous acts: {previous_acts}
Previous scenes: {previous_scenes}

EXAMPLE RESPONSE:
DESCRIPTION:
This act serves as the catalyst for the story's central conflict, introducing the main characters and their initial motivations. It establishes the world and sets up the dramatic tension that will drive the narrative forward.

KEY EVENTS:
1. The protagonist discovers a mysterious artifact that changes their life.
2. The antagonist reveals their true intentions to the protagonist.
3. A key supporting character is introduced and forms an alliance with the protagonist.
4. The first major conflict occurs between the protagonist and antagonist.
5. The act concludes with a revelation that changes the protagonist's understanding of their situation.

CHARACTER DEVELOPMENT:
The protagonist begins as naive and uncertain, but the events of this act force them to confront their fears and begin their journey of growth. The antagonist's true nature is revealed, showing their complexity and motivation.

THEMATIC ELEMENTS:
This act explores themes of discovery, betrayal, and the beginning of transformation. It sets up the central themes that will be developed throughout the story."""

# Create a dictionary of all prompt templates
PROMPT_TEMPLATES = {
    "scene_generation": SCENE_GENERATION_PROMPT,
    "scene_development": SCENE_DEVELOPMENT_PROMPT,
    "scene_improvement": SCENE_IMPROVEMENT_PROMPT,
    "act_planning_advisor": ACT_PLANNING_ADVISOR_PROMPT,
    "act_planning_synthesis": ACT_PLANNING_SYNTHESIS_PROMPT
} 