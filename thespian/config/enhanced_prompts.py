"""
Enhanced prompts for generating longer, more detailed scenes.
"""

# Base scene generation prompt with length emphasis
ENHANCED_SCENE_PROMPT = """
You are a master playwright creating a rich, detailed theatrical scene. Your scene MUST be at least {word_count} words ({char_count} characters) long.

REQUIREMENTS:
1. LENGTH: This is critical - the scene must be AT LEAST {char_count} characters
2. Include extensive stage directions describing:
   - Physical actions and gestures
   - Facial expressions and micro-expressions  
   - Environmental details and atmosphere
   - Lighting and sound cues
   - Character positioning and movement
3. Add subtext through:
   - Pauses and silences
   - Contradictions between words and actions
   - Physical reactions during dialogue
   - Internal emotional states (in parentheticals)
4. Layer in technical elements:
   - Specific lighting states and changes
   - Sound effects and ambient noise
   - Music cues where appropriate
   - Prop interactions
5. Create rich atmosphere through:
   - Sensory details (sights, sounds, smells, textures)
   - Weather and environmental effects
   - Time of day and its effects
   - The emotional resonance of the space

STRUCTURE:
- Start with a detailed atmospheric opening (at least 200 words)
- Alternate between dialogue and substantial stage directions
- Include at least 3-4 lines of stage direction for every 5-6 lines of dialogue
- End with a powerful image or moment (at least 150 words)

Remember: Every line should advance character, plot, or atmosphere. No filler, but rich, meaningful detail that actors and directors can use.

SCENE CONTEXT:
{scene_context}

Write the complete scene now, ensuring it meets the {char_count} character minimum:
"""

# Character-specific dialogue prompt
ENHANCED_CHARACTER_DIALOGUE_PROMPT = """
Write dialogue for {character_name} that reveals multiple layers:

1. SURFACE: What they're literally saying
2. SUBTEXT: What they really mean
3. DESIRE: What they want in this moment
4. FEAR: What they're afraid of revealing
5. TACTIC: How they're trying to get what they want

For each line, include:
- Specific delivery notes (pace, tone, volume)
- Physical actions while speaking
- Where their attention goes
- What they're NOT saying

Make the dialogue feel lived-in and real, with:
- Interruptions and overlaps
- Incomplete thoughts
- Repetitions when emotional
- Silences that speak volumes

Character context: {character_info}
Scene context: {scene_context}

Generate at least {line_count} substantial lines with full performance notes:
"""

# Atmosphere and staging prompt
ENHANCED_ATMOSPHERE_PROMPT = """
Create a rich, theatrical atmosphere for this moment in the scene:

Location: {location}
Time: {time_of_day}
Emotional tone: {emotional_tone}

Include ALL of the following elements:

1. VISUAL ATMOSPHERE (minimum 100 words):
   - Specific lighting (color, intensity, direction, quality)
   - Shadows and what they reveal/hide
   - How the space looks from different angles
   - Visual metaphors for the emotional state

2. AUDITORY LANDSCAPE (minimum 80 words):
   - Ambient sounds and their sources
   - How sound changes through the scene
   - Silence and what it means
   - Off-stage sounds that comment on the action

3. PHYSICAL ENVIRONMENT (minimum 100 words):
   - Temperature and air quality
   - Textures and surfaces
   - How the space has been used/lived in
   - Objects that tell stories

4. TEMPORAL ELEMENTS (minimum 60 words):
   - How time feels in this moment
   - Changes in light/shadow as time passes
   - Rhythms and repetitions
   - The weight of past and future

5. EMOTIONAL GEOGRAPHY (minimum 80 words):
   - How the space reflects internal states
   - Territories and boundaries
   - Safe spaces and danger zones
   - How emotion changes the perception of space

Create a fully realized theatrical environment:
"""

# Technical elements prompt
ENHANCED_TECHNICAL_PROMPT = """
Design comprehensive technical elements for this scene section:

Scene context: {scene_context}
Emotional arc: {emotional_arc}

Provide detailed specifications for:

1. LIGHTING DESIGN:
   - General wash (color temperature, intensity, coverage)
   - Specials (specific instruments for key moments)
   - Transitions (timing, motivation, emotional effect)
   - Practicals (on-stage light sources)
   - Effects (gobos, fog/haze, projections)
   
   Format each cue as:
   LX Q#: [Trigger] - [Description] - [Timing] - [Emotional intent]

2. SOUND DESIGN:
   - Ambient bed (continuous environmental sound)
   - Spot effects (specific moments)
   - Transitions (bridging between states)
   - Off-stage sounds (world beyond the scene)
   - Music/underscoring (if any)
   
   Format each cue as:
   SQ Q#: [Trigger] - [Description] - [Level] - [Speaker placement]

3. SCENIC ELEMENTS:
   - Automated/moving pieces
   - Reveals or transformations
   - Practical effects
   - Flying elements
   
4. COSTUME/MAKEUP:
   - Quick changes needed
   - Reveal moments
   - Distressing or effects
   - Any rigging needs

5. PROPS:
   - Specific handling notes
   - Preset locations
   - Any effects or gimmicks
   - Backup/safety requirements

Be specific enough that a professional crew could execute this design:
"""

# Subtext and internal life prompt
ENHANCED_SUBTEXT_PROMPT = """
For this dialogue exchange, create rich subtext and internal life:

DIALOGUE:
{dialogue_text}

For EACH line, provide:

1. INTERNAL MONOLOGUE (what they're really thinking):
   - Stream of consciousness
   - Memories triggered
   - Judgments and assessments
   - Desires and fears

2. PHYSICAL LIFE (what the body is doing):
   - Micro-expressions
   - Unconscious gestures
   - Where tension is held
   - Breathing patterns

3. EMOTIONAL UNDERSCORING (the feeling beneath):
   - Primary emotion
   - Conflicting emotions
   - Emotional transitions
   - Defense mechanisms

4. RELATIONAL DYNAMICS (how they relate to others):
   - Power plays
   - Intimacy/distance
   - Status negotiations
   - Historical patterns

5. ACTABLE CHOICES (specific performance notes):
   - Operative words
   - Pace and rhythm
   - Physical score
   - Vocal choices

Format as interlinear notes that an actor could use:
"""

# Scene expansion prompt
SCENE_EXPANSION_PROMPT = """
This scene needs to be expanded to at least {target_length} characters (currently {current_length}).

ORIGINAL SCENE:
{original_scene}

Expand this scene by adding:

1. OPENING EXPANSION (add 300+ chars):
   - Detailed atmospheric setup
   - Character preparations/rituals
   - The world before dialogue begins
   - Establishing physical relationships

2. BETWEEN DIALOGUE (add 150+ chars per exchange):
   - Reactions and processing
   - Physical adjustments
   - Environmental interactions
   - Subtext made physical

3. CRISIS ELABORATION (add 400+ chars):
   - Slow down crucial moments
   - Multiple physical/emotional beats
   - The full weight of realization
   - How the world changes

4. RESOLUTION DEEPENING (add 300+ chars):
   - Don't rush the ending
   - Let consequences settle
   - Final images that resonate
   - The new reality establishing

Maintain the original dialogue and structure while adding rich theatrical detail. Every addition should be playable and meaningful.

Expanded scene:
"""

# Integration prompt for combining all elements
INTEGRATION_PROMPT = """
Integrate all the following elements into a cohesive, detailed scene:

DIALOGUE AND ACTION:
{basic_scene}

ATMOSPHERE NOTES:
{atmosphere}

TECHNICAL ELEMENTS:
{technical}

SUBTEXT LAYERS:
{subtext}

CHARACTER DETAILS:
{character_details}

Create a unified scene that:
1. Weaves all elements naturally
2. Maintains dramatic flow
3. Reaches at least {target_length} characters
4. Feels organic, not overstuffed
5. Gives actors and directors rich material

The final scene should feel like a lived experience, not a technical document. Every detail should serve the story and characters.

Integrated scene:
"""


def get_enhanced_scene_prompt(word_count: int = 1500, scene_context: str = "") -> str:
    """Get the enhanced scene generation prompt with specific length requirements."""
    char_count = word_count * 5  # Approximate chars per word
    return ENHANCED_SCENE_PROMPT.format(
        word_count=word_count,
        char_count=char_count,
        scene_context=scene_context
    )


def get_expansion_prompt(original_scene: str, target_length: int) -> str:
    """Get prompt for expanding an existing scene."""
    current_length = len(original_scene)
    return SCENE_EXPANSION_PROMPT.format(
        original_scene=original_scene,
        current_length=current_length,
        target_length=target_length
    )


def get_character_dialogue_prompt(character_name: str, character_info: str, 
                                 scene_context: str, line_count: int = 10) -> str:
    """Get enhanced character dialogue prompt."""
    return ENHANCED_CHARACTER_DIALOGUE_PROMPT.format(
        character_name=character_name,
        character_info=character_info,
        scene_context=scene_context,
        line_count=line_count
    )


def get_atmosphere_prompt(location: str, time_of_day: str, emotional_tone: str) -> str:
    """Get atmosphere generation prompt."""
    return ENHANCED_ATMOSPHERE_PROMPT.format(
        location=location,
        time_of_day=time_of_day,
        emotional_tone=emotional_tone
    )


def get_technical_prompt(scene_context: str, emotional_arc: str) -> str:
    """Get technical elements prompt."""
    return ENHANCED_TECHNICAL_PROMPT.format(
        scene_context=scene_context,
        emotional_arc=emotional_arc
    )


def get_subtext_prompt(dialogue_text: str) -> str:
    """Get subtext enhancement prompt."""
    return ENHANCED_SUBTEXT_PROMPT.format(dialogue_text=dialogue_text)


def get_integration_prompt(basic_scene: str, atmosphere: str, technical: str,
                         subtext: str, character_details: str, target_length: int) -> str:
    """Get integration prompt for combining all elements."""
    return INTEGRATION_PROMPT.format(
        basic_scene=basic_scene,
        atmosphere=atmosphere,
        technical=technical,
        subtext=subtext,
        character_details=character_details,
        target_length=target_length
    )