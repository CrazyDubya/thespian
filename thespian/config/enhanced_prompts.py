"""Enhanced prompt templates for scene generation and processing."""

from typing import Dict

ENHANCED_SCENE_GENERATION_PROMPT = """Generate a highly detailed and immersive theatrical scene for {title} following this outline:

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

FORMATTING REQUIREMENTS:
1. Character names must be in ALL CAPS
2. Stage directions must be in (parentheses)
3. Each character's dialogue must be on a new line
4. Stage directions must be on their own lines
5. Technical cues (LIGHTS, SOUND, etc.) must be in [brackets]
6. No markdown formatting
7. No bold or italic text
8. No special characters except for standard punctuation
9. Each line of dialogue MUST be followed by detailed stage directions
10. Each stage direction MUST include both physical actions AND emotional states
11. Each technical cue MUST be specific and atmospheric
12. Each character interaction MUST show both external dialogue and internal thoughts
13. Each scene transition MUST be clearly marked with technical cues

ADVANCED THEATRICAL REQUIREMENTS:
1. Include at least three moments of subtext (characters saying one thing but meaning another)
2. Create at least one moment of profound emotional vulnerability for a character
3. Develop multiple levels of conflict (internal, interpersonal, and situational)
4. Create contrasting emotional states between characters
5. Include meaningful use of silence or pauses for dramatic effect
6. Use staging and physical positioning to reflect power dynamics
7. Create symbolic or metaphorical elements that reinforce themes
8. Include sensory details from at least three senses (sight, sound, smell, touch, taste)
9. Develop the scene's atmosphere through environmental details
10. Show character development through changing behavior or perspective

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

ITERATIVE_SCENE_REFINEMENT_PROMPT = """Refine and enhance this scene based on previous evaluation. This is iteration {iteration_number} of the refinement process.

Current Scene:
{scene_content}

Quality Evaluation:
{evaluation}

Previous Iterations:
{previous_iterations}

Focus Areas for This Iteration:
{focus_areas}

REFINEMENT REQUIREMENTS:
1. Maintain the scene's core narrative structure and key events
2. Address ALL specific issues identified in the evaluation
3. Concentrate especially on the Focus Areas for this iteration
4. Expand and deepen elements that scored below 0.7 in the evaluation
5. Maintain or improve elements that scored above 0.7
6. Ensure the scene length remains between {min_length}-{max_length} characters
7. Do not introduce new plot elements that would create continuity issues
8. Ensure all characters maintain consistent personality and motivation
9. Preserve any particularly strong elements from the current scene

ADVANCED ENHANCEMENT GUIDANCE:
1. For character development issues:
   - Add more internal thoughts and reactions
   - Develop more nuanced emotional responses
   - Create more specific physical mannerisms
   - Deepen character motivations and conflicts

2. For dialogue issues:
   - Create more distinctive voices for each character
   - Add more subtext and layered meaning
   - Vary sentence structure and rhythm
   - Develop more natural conversational flow

3. For technical issues:
   - Increase specificity of stage directions
   - Add more atmospheric lighting and sound cues
   - Create more detailed prop utilization
   - Develop more dynamic staging

4. For thematic issues:
   - Strengthen symbolic elements
   - Deepen thematic exploration through dialogue
   - Create visual metaphors in staging
   - Develop thematic contrasts between characters

5. For pacing issues:
   - Add more tension building elements
   - Create more varied emotional rhythms
   - Develop clearer dramatic beats
   - Improve scene structure and flow

Format your response EXACTLY as follows:

REFINED SCENE:
[Your refined scene content]

REFINEMENT ANALYSIS:
1. Specific improvements made in this iteration
2. How evaluation issues were addressed
3. Elements preserved from the original scene
4. Overall enhancement strategy used"""

SCENE_EXPANSION_PROMPT = """Significantly expand and deepen this scene while maintaining its core narrative. The current scene is {current_length} characters, but I need a highly detailed scene of at least {target_length} characters.

Current Scene:
{scene}

EXPANSION REQUIREMENTS:

1. Emotional and Psychological Depth:
   - Add extended internal monologues for characters revealing thoughts/feelings
   - Include detailed emotional reactions to events
   - Show psychological complexity through conflicting feelings
   - Reveal backstory elements through memories triggered by events

2. Environmental and Sensory Detail:
   - Add rich sensory descriptions for each location (sight, sound, smell, touch)
   - Describe subtle environmental changes throughout the scene
   - Include detailed prop descriptions and how characters interact with them
   - Create atmospheric elements that reflect the emotional tone

3. Character Physical Expression:
   - Expand descriptions of facial expressions and micro-expressions
   - Detail physical mannerisms unique to each character
   - Include subtle body language that reveals character psychology
   - Show physiological responses to emotions (racing heart, etc.)

4. Dialogue Enhancement:
   - Extend dialogue exchanges with realistic back-and-forth
   - Add subtext to dialogue (saying one thing, meaning another)
   - Include pauses, stammers, and natural speech patterns
   - Show contrasting communication styles between characters

5. Thematic and Symbolic Elements:
   - Develop recurring motifs and symbols
   - Incorporate metaphorical elements that reflect themes
   - Weave thematic questions into dialogue and action
   - Create parallel situations that explore themes from different angles

IMPORTANT: Maintain coherence with the original scene's key events and character motivations while significantly expanding the detail, depth, and length.

Format your response EXACTLY as follows:

EXPANDED SCENE:
[Your expanded scene content]

EXPANSION ANALYSIS:
1. Original vs. new length and why this serves the scene
2. Key elements expanded and how they enhance the scene
3. How the expansion maintains coherence with the original scene
4. How the expansion develops characters beyond the original scene
5. How the expansion enriches thematic elements"""

CHARACTER_DEPTH_PROMPT = """Enhance the character depth in this scene while maintaining narrative coherence. The goal is to make each character feel fully three-dimensional.

Current Scene:
{scene}

Character Profiles:
{character_profiles}

ENHANCEMENT REQUIREMENTS:

1. Character History Integration:
   - Weave subtle references to each character's backstory
   - Include dialogue that references shared history
   - Add thoughts that reveal key formative experiences
   - Show how past experiences influence current reactions

2. Psychological Complexity:
   - Show conflicting desires and motivations
   - Include moral dilemmas and internal conflict
   - Reveal contradictions between thoughts and actions
   - Show coping mechanisms and defense strategies

3. Relationship Dynamics:
   - Develop complex power dynamics between characters
   - Show varied relationship tensions
   - Include subtle callbacks to previous interactions
   - Demonstrate character growth through relationship changes

4. Character-Specific Speech and Movement:
   - Distinctive vocabulary and speech patterns for each character
   - Unique physical mannerisms and gestures
   - Character-specific emotional expressions
   - Consistent but evolving behavioral patterns

5. Subtle Character Development:
   - Small but meaningful changes in perspective
   - Moments of self-awareness or realization
   - Tests of character values and principles
   - Growth opportunities through challenges

Format your response EXACTLY as follows:

ENHANCED SCENE:
[Your enhanced scene content]

CHARACTER ENHANCEMENT ANALYSIS:
[For each character, explain how they've been deepened]"""

COLLABORATIVE_SYNTHESIS_PROMPT = """Synthesize these component contributions into a unified, coherent scene that exceeds the sum of its parts.

Component 1 (Dialogue): {dialogue_content}
Component 2 (Narrative): {narrative_content}
Component 3 (Technical): {technical_content}
Component 4 (Emotional): {emotional_content}

Requirements: {requirements}

SYNTHESIS GUIDELINES:

1. Narrative Integration:
   - Seamlessly weave all components into a unified whole
   - Ensure consistent story progression and pacing
   - Maintain coherent cause-and-effect relationships
   - Preserve the unique strengths of each component

2. Dramatic Enhancement:
   - Identify and amplify key dramatic moments
   - Create clear beginning, middle, and end structure
   - Develop rising action and meaningful resolution
   - Balance focus between characters and plot

3. Component Harmonization:
   - Resolve any contradictions between components
   - Blend tonal variations into a consistent atmosphere
   - Create smooth transitions between dialog-heavy and description-heavy sections
   - Balance emotional, technical, and narrative elements

4. Creative Elevation:
   - Add unifying thematic elements that tie components together
   - Enhance emotional impact by connecting related elements
   - Develop recurring motifs across components
   - Create meaningful connections between seemingly disparate elements

Format your response EXACTLY as follows:

SYNTHESIZED SCENE:
[Your synthesized scene content]

SYNTHESIS ANALYSIS:
1. How components were integrated
2. How contradictions were resolved
3. How the synthesis enhances the overall impact
4. How the synthesis preserves the strengths of individual components"""

LLM_EVALUATION_PROMPT = """Perform a detailed theatrical quality evaluation of this scene.

SCENE CONTENT:
{scene}

REQUIREMENTS:
{requirements}

Evaluate each of the following dimensions on a scale from 0.0 to 1.0 with detailed feedback:

1. Character Depth (0.0-1.0):
   - How fully developed are the characters?
   - Do they have clear motivations and psychological complexity?
   - Are their reactions consistent with their established traits?
   - Do they show internal thoughts and emotional depth?

2. Dialogue Quality (0.0-1.0):
   - How natural and distinctive is the dialogue?
   - Does each character have a unique voice?
   - Is there subtext and layered meaning?
   - Does dialogue advance plot and reveal character?

3. Plot Coherence (0.0-1.0):
   - Does the scene advance the plot meaningfully?
   - Are cause-and-effect relationships clear?
   - Does the scene maintain continuity with previous events?
   - Does it set up future developments effectively?

4. Dramatic Structure (0.0-1.0):
   - Does the scene have a clear beginning, middle, and end?
   - Is there rising tension and meaningful resolution?
   - Are there effective dramatic beats?
   - Does the pacing serve the content?

5. Technical Execution (0.0-1.0):
   - How effectively are stage directions utilized?
   - Are lighting and sound cues integrated meaningfully?
   - Are props used purposefully?
   - Is the staging dynamic and meaningful?

6. Thematic Depth (0.0-1.0):
   - How effectively are themes explored?
   - Are there symbolic or metaphorical elements?
   - Do character journeys reflect thematic concerns?
   - Is the thematic content consistent with the play's overall themes?

7. Sensory Immersion (0.0-1.0):
   - How effectively does the scene engage multiple senses?
   - Is the environment richly detailed?
   - Are atmospheric elements present?
   - Can readers visualize the setting clearly?

8. Emotional Impact (0.0-1.0):
   - How emotionally engaging is the scene?
   - Are there moments of genuine emotional power?
   - Does the scene evoke specific emotional responses?
   - Is there emotional depth and complexity?

For each dimension, provide:
1. A numerical score from 0.0 to 1.0
2. 2-3 specific strengths
3. 2-3 specific areas for improvement
4. 1-2 concrete suggestions for enhancing this dimension

Format your response as detailed JSON with these categories and subcategories."""

# Create a dictionary of all prompt templates
ENHANCED_PROMPT_TEMPLATES = {
    "enhanced_scene_generation": ENHANCED_SCENE_GENERATION_PROMPT,
    "iterative_scene_refinement": ITERATIVE_SCENE_REFINEMENT_PROMPT,
    "scene_expansion": SCENE_EXPANSION_PROMPT,
    "character_depth": CHARACTER_DEPTH_PROMPT,
    "collaborative_synthesis": COLLABORATIVE_SYNTHESIS_PROMPT,
    "llm_evaluation": LLM_EVALUATION_PROMPT
}