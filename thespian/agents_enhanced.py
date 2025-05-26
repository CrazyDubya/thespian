"""
Enhanced agent methods for rich multi-agent collaboration.
These methods extend the base agent classes with collaborative capabilities.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import Field
import json
import re

from .agents import DirectorAgent, CharacterActorAgent, SetCostumeDesignAgent, StageManagerAgent


class EnhancedDirectorAgent(DirectorAgent):
    """Director agent with enhanced collaborative methods."""
    
    def provide_scene_notes(self, scene: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Provide specific, actionable feedback on a scene."""
        prompt = f"""You are a theatre director reviewing a scene. Provide specific, actionable feedback.

SCENE REQUIREMENTS:
Setting: {requirements.get('setting')}
Style: {requirements.get('style')}
Emotional Arc: {requirements.get('emotional_arc')}
Key Conflict: {requirements.get('key_conflict')}

SCENE CONTENT:
{scene}

Provide feedback in this JSON format:
{{
    "overall_assessment": "Brief overall impression",
    "strengths": ["What works well"],
    "specific_notes": [
        {{"line_reference": "Quote or line number", "issue": "What needs work", "suggestion": "Specific fix"}},
    ],
    "pacing_notes": "Comments on rhythm and pacing",
    "emotional_notes": "Comments on emotional journey",
    "staging_suggestions": ["Specific staging ideas"],
    "priority_revisions": ["Most important changes needed"]
}}"""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        try:
            return json.loads(content)
        except:
            # Fallback structure
            return {
                "overall_assessment": content,
                "specific_notes": [],
                "priority_revisions": ["Review director feedback manually"]
            }
    
    def workshop_scene(self, scene: str, actors: List['EnhancedCharacterActorAgent']) -> Dict[str, Any]:
        """Lead a workshop session with actors to develop the scene."""
        workshop_results = {
            "director_vision": self._articulate_vision(scene),
            "actor_insights": {},
            "collaborative_improvements": [],
            "workshopped_moments": []
        }
        
        # Get each actor's perspective
        for actor in actors:
            if actor.character_name in scene:
                insights = actor.explore_character_moment(scene)
                workshop_results["actor_insights"][actor.character_name] = insights
        
        # Synthesize collaborative improvements
        prompt = f"""As a director, synthesize the actor insights into collaborative improvements:

Scene: {scene[:1000]}...

Actor Insights: {json.dumps(workshop_results["actor_insights"], indent=2)}

Create specific improvements that honor both directorial vision and actor insights."""
        
        response = self.llm.invoke(prompt)
        workshop_results["collaborative_improvements"] = response.content if hasattr(response, 'content') else str(response)
        
        return workshop_results
    
    def _articulate_vision(self, scene: str) -> str:
        """Articulate the director's vision for the scene."""
        prompt = f"As a director, what is your vision for this scene's emotional journey and staging? Scene: {scene[:500]}..."
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


class EnhancedCharacterActorAgent(CharacterActorAgent):
    """Character actor agent with enhanced collaborative methods."""
    
    def suggest_dialogue_improvements(self, scene: str, character_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest character-specific dialogue improvements."""
        prompt = f"""You are an actor playing {self.character_name}. Review this scene and suggest dialogue improvements.

CHARACTER PROFILE:
Background: {character_profile.get('background')}
Motivations: {character_profile.get('motivations')}
Relationships: {character_profile.get('relationships')}
Current Arc Stage: {character_profile.get('development_arc', [{}])[-1].get('description', 'Unknown')}

SCENE:
{scene}

For each of your character's lines, suggest improvements that:
1. Better reflect their personality and background
2. Advance their character arc
3. Create subtext and layers
4. Feel authentic to their relationships

Format as JSON:
[
    {{
        "original_line": "The exact line from the scene",
        "improved_line": "Your suggested improvement",
        "reasoning": "Why this change serves the character",
        "subtext": "What the character really means"
    }}
]"""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        try:
            return json.loads(content)
        except:
            return []
    
    def validate_character_consistency(self, scene: str, previous_scenes: List[str] = None) -> Dict[str, Any]:
        """Ensure character stays true across scenes."""
        context = ""
        if previous_scenes:
            context = f"Previous scene excerpts: {' '.join([s[:200] for s in previous_scenes[-2:]])}"
        
        prompt = f"""As an actor playing {self.character_name}, check if this character stays consistent.

{context}

CURRENT SCENE:
{scene}

Analyze:
1. Does the character's voice remain consistent?
2. Do their actions align with established motivations?
3. Are relationships portrayed consistently?
4. Is their emotional state believable given previous scenes?

Format response as JSON:
{{
    "consistency_score": 0-1,
    "voice_consistency": "Analysis",
    "motivation_alignment": "Analysis",
    "relationship_consistency": "Analysis",
    "emotional_continuity": "Analysis",
    "specific_inconsistencies": ["List any specific issues"],
    "suggestions": ["How to fix inconsistencies"]
}}"""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        try:
            return json.loads(content)
        except:
            return {"consistency_score": 0.5, "analysis": content}
    
    def develop_subtext(self, dialogue_line: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add layers of meaning to dialogue."""
        prompt = f"""As {self.character_name}, develop the subtext for this line.

Context: {json.dumps(context, indent=2)}
Line: "{dialogue_line}"

What is the character:
1. Actually saying (text)
2. Really meaning (subtext)
3. Hiding or avoiding
4. Physically doing while speaking
5. Emotionally experiencing

Provide rich, layered interpretation."""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "line": dialogue_line,
            "subtext": content,
            "physical_action": self._suggest_physical_action(dialogue_line, context),
            "emotional_state": self._analyze_emotional_state(dialogue_line, context)
        }
    
    def explore_character_moment(self, scene: str) -> Dict[str, Any]:
        """Deep dive into a character's key moment in the scene."""
        prompt = f"""As {self.character_name}, identify and explore your most important moment in this scene.

SCENE: {scene}

Analyze:
1. What is your character's most vulnerable/powerful moment?
2. What are they fighting for in this moment?
3. What memories or experiences inform this moment?
4. How does this moment change them?
5. What physical life accompanies this moment?"""
        
        response = self.llm.invoke(prompt)
        return {
            "character": self.character_name,
            "key_moment_analysis": response.content if hasattr(response, 'content') else str(response)
        }
    
    def _suggest_physical_action(self, line: str, context: Dict[str, Any]) -> str:
        """Suggest physical actions that reveal character."""
        prompt = f"As {self.character_name}, what physical action reveals your inner state while saying: '{line}'?"
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _analyze_emotional_state(self, line: str, context: Dict[str, Any]) -> str:
        """Analyze the emotional state behind the line."""
        prompt = f"As {self.character_name}, what emotions are you experiencing (not showing) while saying: '{line}'?"
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


class EnhancedSetCostumeDesignAgent(SetCostumeDesignAgent):
    """Designer agent with enhanced collaborative methods."""
    
    def suggest_scene_elements(self, requirements: Dict[str, Any], scene_mood: str) -> Dict[str, Any]:
        """Suggest visual elements during scene writing, not after."""
        prompt = f"""As a theatrical designer, suggest visual elements that enhance this scene.

REQUIREMENTS:
Setting: {requirements.get('setting')}
Period: {requirements.get('period')}
Style: {requirements.get('style')}
Mood: {scene_mood}

Provide specific suggestions for:
1. Lighting to enhance emotional journey
2. Set pieces that support action
3. Costume details that reveal character
4. Props that add meaning
5. Sound/music to underscore moments

Format as detailed production notes."""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        return self._parse_design_elements(content)
    
    def create_atmosphere_notes(self, scene_content: str, emotional_arc: str) -> Dict[str, Any]:
        """Create detailed atmosphere and mood notes."""
        prompt = f"""Design the atmosphere for this scene to support its emotional arc.

EMOTIONAL ARC: {emotional_arc}
SCENE EXCERPT: {scene_content[:1000]}...

Create specific notes for:
1. Color palette evolution through scene
2. Lighting transitions with emotional beats
3. Sound landscape and its changes
4. Spatial relationships and their meaning
5. Textural elements (rough/smooth, hard/soft)

Be specific with cue points and transitions."""
        
        response = self.llm.invoke(prompt)
        return {
            "atmosphere_design": response.content if hasattr(response, 'content') else str(response),
            "key_transitions": self._identify_transition_points(scene_content)
        }
    
    def integrate_with_action(self, scene: str, staging_notes: List[str]) -> List[Dict[str, Any]]:
        """Integrate design elements with specific scene moments."""
        integrated_elements = []
        
        # Find key moments in the scene
        key_moments = self._identify_key_moments(scene)
        
        for moment in key_moments:
            prompt = f"""For this moment in the scene:
{moment}

How can design enhance it? Consider:
- Lighting shift
- Sound cue
- Prop interaction
- Costume reveal/change
- Set transformation"""
            
            response = self.llm.invoke(prompt)
            integrated_elements.append({
                "moment": moment,
                "design_enhancement": response.content if hasattr(response, 'content') else str(response)
            })
        
        return integrated_elements
    
    def _parse_design_elements(self, content: str) -> Dict[str, Any]:
        """Parse design content into structured format."""
        return {
            "lighting": self._extract_section(content, "lighting"),
            "set": self._extract_section(content, "set"),
            "costumes": self._extract_section(content, "costume"),
            "props": self._extract_section(content, "props"),
            "sound": self._extract_section(content, "sound")
        }
    
    def _extract_section(self, content: str, section: str) -> str:
        """Extract a section from design notes."""
        pattern = rf"{section}.*?:(.*?)(?=\n\d+\.|$)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _identify_key_moments(self, scene: str) -> List[str]:
        """Identify key moments in the scene for design enhancement."""
        # Simple heuristic: find emotional peaks, entrances/exits, revelations
        moments = []
        lines = scene.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['enter', 'exit', 'reveal', 'discover', 'realize']):
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                moments.append(context)
        return moments[:5]  # Limit to 5 key moments
    
    def _identify_transition_points(self, scene: str) -> List[Dict[str, Any]]:
        """Identify emotional transition points for design changes."""
        # This would be more sophisticated in production
        return [
            {"point": "Opening", "type": "establishing"},
            {"point": "First conflict", "type": "tension"},
            {"point": "Emotional peak", "type": "climax"},
            {"point": "Resolution", "type": "denouement"}
        ]


class EnhancedStageManagerAgent(StageManagerAgent):
    """Stage Manager agent with enhanced collaborative methods."""
    
    def check_continuity(self, current_scene: str, previous_scenes: List[Dict[str, Any]], 
                        production_bible: Dict[str, Any]) -> Dict[str, Any]:
        """Check for continuity errors across scenes."""
        continuity_report = {
            "continuity_errors": [],
            "warnings": [],
            "tracked_elements": {},
            "suggestions": []
        }
        
        # Build context from previous scenes
        context = self._build_continuity_context(previous_scenes)
        
        prompt = f"""As a stage manager, check this scene for continuity errors.

ESTABLISHED CONTEXT:
{json.dumps(context, indent=2)}

CURRENT SCENE:
{current_scene}

Check for:
1. Prop continuity (items mentioned should exist/persist correctly)
2. Costume continuity (changes should be noted)
3. Character positioning (where did they enter from?)
4. Time continuity (does timing make sense?)
5. Injury/state continuity (wounds, exhaustion, etc.)
6. Information continuity (what do characters know?)

Report any issues found."""
        
        response = self.llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Parse response and structure report
        continuity_report["analysis"] = content
        continuity_report["tracked_elements"] = self._extract_trackable_elements(current_scene)
        
        return continuity_report
    
    def track_technical_elements(self, scene: str) -> Dict[str, Any]:
        """Track all technical elements in a scene."""
        elements = {
            "props": self._extract_props(scene),
            "costumes": self._extract_costume_notes(scene),
            "sound_cues": self._extract_sound_cues(scene),
            "lighting_cues": self._extract_lighting_cues(scene),
            "entrances_exits": self._extract_blocking(scene),
            "set_pieces": self._extract_set_pieces(scene)
        }
        
        # Create technical running order
        prompt = f"""Create a technical running order for this scene:
{scene[:1500]}...

List all cues in order with timing estimates."""
        
        response = self.llm.invoke(prompt)
        elements["running_order"] = response.content if hasattr(response, 'content') else str(response)
        
        return elements
    
    def coordinate_scene_changes(self, current_scene_tech: Dict[str, Any], 
                                next_scene_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan transitions between scenes."""
        prompt = f"""Plan the transition from current scene to next.

CURRENT SCENE ENDS WITH:
{json.dumps(current_scene_tech, indent=2)}

NEXT SCENE REQUIRES:
{json.dumps(next_scene_requirements, indent=2)}

Create transition plan including:
1. What needs to be struck/removed
2. What needs to be added/set
3. Transition music/lighting
4. Time estimate
5. Crew assignments"""
        
        response = self.llm.invoke(prompt)
        return {
            "transition_plan": response.content if hasattr(response, 'content') else str(response),
            "estimated_time": "45 seconds",
            "crew_needed": 3
        }
    
    def generate_rehearsal_schedule(self, scenes: List[Dict[str, Any]], 
                                   cast_availability: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an efficient rehearsal schedule."""
        prompt = f"""Create a rehearsal schedule for these scenes:
{json.dumps([{"scene": s.get("title"), "characters": s.get("characters")} for s in scenes], indent=2)}

Cast availability:
{json.dumps(cast_availability, indent=2)}

Optimize for:
1. Actor availability
2. Scene complexity (complex scenes need more time)
3. Character development (rehearse in arc order when possible)
4. Technical requirements"""
        
        response = self.llm.invoke(prompt)
        return {
            "schedule": response.content if hasattr(response, 'content') else str(response),
            "total_hours_needed": self._estimate_rehearsal_time(scenes)
        }
    
    def _build_continuity_context(self, previous_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context from previous scenes for continuity checking."""
        context = {
            "established_props": [],
            "character_states": {},
            "established_facts": [],
            "time_progression": []
        }
        
        for scene in previous_scenes:
            # Extract relevant continuity information
            if "props" in scene:
                context["established_props"].extend(scene["props"])
            if "character_states" in scene:
                context["character_states"].update(scene["character_states"])
        
        return context
    
    def _extract_props(self, scene: str) -> List[str]:
        """Extract prop references from scene."""
        # Simple pattern matching - would be more sophisticated in production
        props = []
        prop_patterns = [r'picks up (\w+)', r'holds (\w+)', r'with (\w+) in hand']
        for pattern in prop_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            props.extend(matches)
        return list(set(props))
    
    def _extract_costume_notes(self, scene: str) -> List[str]:
        """Extract costume references."""
        costume_patterns = [r'wearing (\w+)', r'dressed in (\w+)', r'changes into (\w+)']
        notes = []
        for pattern in costume_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            notes.extend(matches)
        return notes
    
    def _extract_sound_cues(self, scene: str) -> List[str]:
        """Extract sound cue references."""
        sound_patterns = [r'\[SOUND: (.*?)\]', r'\[Sound: (.*?)\]']
        cues = []
        for pattern in sound_patterns:
            matches = re.findall(pattern, scene)
            cues.extend(matches)
        return cues
    
    def _extract_lighting_cues(self, scene: str) -> List[str]:
        """Extract lighting cue references."""
        lighting_patterns = [r'\[LIGHTS?: (.*?)\]', r'\[Lighting: (.*?)\]']
        cues = []
        for pattern in lighting_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            cues.extend(matches)
        return cues
    
    def _extract_blocking(self, scene: str) -> List[Dict[str, str]]:
        """Extract entrance and exit information."""
        blocking = []
        entrance_patterns = [r'(\w+) enters', r'Enter (\w+)', r'(\w+) walks in']
        exit_patterns = [r'(\w+) exits', r'Exit (\w+)', r'(\w+) leaves']
        
        for pattern in entrance_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            for match in matches:
                blocking.append({"character": match, "action": "entrance"})
                
        for pattern in exit_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            for match in matches:
                blocking.append({"character": match, "action": "exit"})
                
        return blocking
    
    def _extract_set_pieces(self, scene: str) -> List[str]:
        """Extract set piece references."""
        # Look for furniture, architectural elements, etc.
        set_patterns = [r'at the (\w+)', r'on the (\w+)', r'by the (\w+)']
        pieces = []
        for pattern in set_patterns:
            matches = re.findall(pattern, scene, re.IGNORECASE)
            pieces.extend(matches)
        return list(set(pieces))
    
    def _extract_trackable_elements(self, scene: str) -> Dict[str, Any]:
        """Extract all elements that need continuity tracking."""
        return {
            "props": self._extract_props(scene),
            "costumes": self._extract_costume_notes(scene),
            "character_positions": self._extract_blocking(scene),
            "established_facts": []  # Would extract plot points, injuries, etc.
        }
    
    def _estimate_rehearsal_time(self, scenes: List[Dict[str, Any]]) -> int:
        """Estimate total rehearsal time needed."""
        # Simple estimation: 2 hours per scene plus complexity factors
        base_time = len(scenes) * 2
        complexity_factor = 1.5  # Would calculate based on scene analysis
        return int(base_time * complexity_factor)