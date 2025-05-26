"""
Demonstration of scene detail enhancement system.
"""

import sys
sys.path.append('.')

from thespian.llm.detail_enhancer import SceneDetailEnhancer, DetailLayer
from thespian.config.enhanced_prompts import (
    get_enhanced_scene_prompt,
    get_expansion_prompt,
    get_atmosphere_prompt,
    get_technical_prompt,
    get_subtext_prompt
)


def demonstrate_scene_analysis():
    """Demonstrate scene analysis capabilities."""
    print("=== Scene Analysis Demo ===\n")
    
    enhancer = SceneDetailEnhancer(target_length=5000)
    
    # Sample short scene
    short_scene = """
ACT 2, SCENE 3

[A coffee shop. EMMA sits alone at a table. DAVID enters.]

DAVID: Is this seat taken?

EMMA: It is now.

DAVID: Emma, we need to talk.

EMMA: No, we don't.

DAVID: Please. Just hear me out.

EMMA: You had your chance to talk. You chose silence.

DAVID: That's not fair.

EMMA: Life isn't fair, David.

[EMMA stands to leave.]

DAVID: I still love you.

[EMMA pauses, then exits without looking back.]
"""
    
    print("Original Scene Length:", len(short_scene), "characters")
    print("-" * 50)
    
    # Analyze the scene
    analysis = enhancer.analyze_scene(short_scene)
    
    print("\nScene Analysis:")
    print(f"- Current length: {analysis['current_length']} characters")
    print(f"- Target length: {enhancer.target_length} characters")
    print(f"- Length deficit: {analysis['length_deficit']} characters")
    print(f"- Dialogue/Direction ratio: {analysis['dialogue_to_direction_ratio']:.2f}")
    
    print("\nStructural Analysis:")
    structure = analysis['structure']
    print(f"- Total lines: {structure['total_lines']}")
    print(f"- Dialogue lines: {structure['dialogue_lines']}")
    print(f"- Stage direction lines: {structure['stage_direction_lines']}")
    print(f"- Characters: {', '.join(structure['character_names'])}")
    print(f"- Technical cues: {structure['technical_cues']}")
    
    print("\nEnhancement Opportunities:")
    for opportunity in analysis['enhancement_opportunities']:
        print(f"- {opportunity}")
    
    return short_scene, analysis


def demonstrate_detail_planning():
    """Demonstrate detail enhancement planning."""
    print("\n\n=== Detail Enhancement Planning ===\n")
    
    enhancer = SceneDetailEnhancer(target_length=5000)
    short_scene, analysis = demonstrate_scene_analysis()
    
    # Create enhancement plan
    detail_plan = enhancer.create_detail_plan(short_scene)
    
    print("Enhancement Plan (by priority):")
    for i, layer in enumerate(detail_plan, 1):
        print(f"{i}. {layer.layer_type.upper()} (Priority: {layer.priority})")
        print(f"   - {layer.content}")
    
    return detail_plan


def demonstrate_enhancement_strategies():
    """Demonstrate different enhancement strategies."""
    print("\n\n=== Enhancement Strategies ===\n")
    
    enhancer = SceneDetailEnhancer()
    
    print("Available Enhancement Strategies:")
    for name, strategy in enhancer.enhancement_strategies.items():
        print(f"\n{name.upper()}:")
        print(f"- Target: {strategy.target_element}")
        print(f"- Min addition length: {strategy.min_addition_length} chars")
        print(f"- Max additions per scene: {strategy.max_additions_per_scene}")
        print("- Sample prompts:")
        for prompt in strategy.enhancement_prompts[:2]:
            print(f"  • {prompt}")


def demonstrate_scene_enhancement():
    """Demonstrate actual scene enhancement."""
    print("\n\n=== Scene Enhancement Demo ===\n")
    
    enhancer = SceneDetailEnhancer(target_length=5000)
    
    original_scene = """
[A park bench. ALEX and JORDAN sit together, not touching.]

ALEX: I got the job.

JORDAN: In Seattle?

ALEX: Yes.

JORDAN: When do you leave?

ALEX: Two weeks.

JORDAN: That's... soon.

ALEX: I know.

[Long pause.]

JORDAN: What about us?

ALEX: I don't know.

JORDAN: You don't know?

ALEX: Jordan...

JORDAN: No, it's fine. Congratulations.

[JORDAN stands.]

ALEX: Wait—

JORDAN: I need some air.

[JORDAN exits. ALEX sits alone.]
"""
    
    print("ORIGINAL SCENE:")
    print("-" * 50)
    print(original_scene)
    print(f"\nOriginal length: {len(original_scene)} characters")
    
    # Enhance the scene
    enhanced_scene = enhancer.enhance_scene(original_scene)
    
    print("\n\nENHANCED SCENE:")
    print("-" * 50)
    print(enhanced_scene)
    print(f"\nEnhanced length: {len(enhanced_scene)} characters")
    print(f"Improvement: {len(enhanced_scene) - len(original_scene)} characters added")
    print(f"Growth factor: {len(enhanced_scene) / len(original_scene):.2f}x")


def demonstrate_specific_enhancements():
    """Demonstrate specific enhancement techniques."""
    print("\n\n=== Specific Enhancement Techniques ===\n")
    
    enhancer = SceneDetailEnhancer()
    
    sample_dialogue = """
SARAH: I'm fine.
MARK: You don't look fine.
SARAH: I said I'm fine.
MARK: Sarah, please talk to me.
SARAH: There's nothing to say.
"""
    
    print("1. SUBTEXT INJECTION:")
    print("-" * 40)
    print("Original:")
    print(sample_dialogue)
    
    with_subtext = enhancer.inject_subtext_layers(sample_dialogue)
    print("\nWith Subtext:")
    print(with_subtext)
    
    # Technical elements
    sample_scene = """
[Living room. Evening.]

JOHN enters.

MARY: You're late.

JOHN: Traffic.

[MARY turns away.]

MARY: Dinner's cold.
"""
    
    print("\n\n2. TECHNICAL ELEMENT EXPANSION:")
    print("-" * 40)
    print("Original:")
    print(sample_scene)
    
    with_technical = enhancer.expand_technical_elements(sample_scene)
    print("\nWith Technical Elements:")
    print(with_technical)


def demonstrate_prompt_generation():
    """Demonstrate enhanced prompt generation."""
    print("\n\n=== Enhanced Prompt Generation ===\n")
    
    print("1. SCENE GENERATION PROMPT (1500 words):")
    print("-" * 50)
    scene_prompt = get_enhanced_scene_prompt(
        word_count=1500,
        scene_context="Two former lovers meet by chance after five years"
    )
    print(scene_prompt[:500] + "...\n")
    
    print("2. ATMOSPHERE PROMPT:")
    print("-" * 50)
    atmosphere_prompt = get_atmosphere_prompt(
        location="abandoned theatre",
        time_of_day="twilight",
        emotional_tone="nostalgic melancholy"
    )
    print(atmosphere_prompt[:400] + "...\n")
    
    print("3. TECHNICAL ELEMENTS PROMPT:")
    print("-" * 50)
    technical_prompt = get_technical_prompt(
        scene_context="emotional reunion scene",
        emotional_arc="tension → recognition → vulnerability → unresolved"
    )
    print(technical_prompt[:400] + "...\n")
    
    print("4. SUBTEXT PROMPT:")
    print("-" * 50)
    subtext_prompt = get_subtext_prompt(
        dialogue_text="ANNA: How have you been?\nBEN: Good. You?\nANNA: Good."
    )
    print(subtext_prompt[:400] + "...")


def demonstrate_length_targeting():
    """Demonstrate targeting specific scene lengths."""
    print("\n\n=== Length Targeting Demo ===\n")
    
    base_scene = """
TOM: I need to tell you something.
LISA: What is it?
TOM: I'm leaving.
LISA: When?
TOM: Tomorrow.
[LISA turns away.]
TOM: Lisa...
LISA: Just go.
"""
    
    print(f"Base scene: {len(base_scene)} characters\n")
    
    # Test different target lengths
    targets = [1000, 3000, 5000]
    
    for target in targets:
        print(f"\nTarget: {target} characters")
        print("-" * 30)
        
        enhancer = SceneDetailEnhancer(target_length=target)
        enhanced = enhancer.enhance_scene(base_scene)
        
        print(f"Achieved: {len(enhanced)} characters")
        print(f"Percentage of target: {(len(enhanced) / target * 100):.1f}%")
        
        # Show sample of enhancement
        if len(enhanced) > len(base_scene):
            new_content = enhanced[len(base_scene):len(base_scene) + 200]
            print(f"Sample addition: ...{new_content}...")


def analyze_enhancement_quality():
    """Analyze the quality of enhancements."""
    print("\n\n=== Enhancement Quality Analysis ===\n")
    
    enhancer = SceneDetailEnhancer(target_length=5000)
    
    test_scene = """
[Office. MANAGER and EMPLOYEE.]

MANAGER: We need to talk about your performance.
EMPLOYEE: Is there a problem?
MANAGER: Several, actually.
EMPLOYEE: I see.
MANAGER: Do you?
EMPLOYEE: I've been trying my best.
MANAGER: Your best isn't good enough.
[EMPLOYEE looks down.]
MANAGER: I'm sorry, but we're letting you go.
EMPLOYEE: Today?
MANAGER: Clear your desk by five.
[MANAGER exits. EMPLOYEE sits in shock.]
"""
    
    # Analyze before and after
    before_analysis = enhancer.analyze_scene(test_scene)
    enhanced_scene = enhancer.enhance_scene(test_scene)
    after_analysis = enhancer.analyze_scene(enhanced_scene)
    
    print("Quality Metrics Comparison:")
    print("-" * 40)
    print(f"{'Metric':<30} {'Before':<15} {'After':<15}")
    print("-" * 40)
    print(f"{'Length (chars)':<30} {before_analysis['current_length']:<15} {after_analysis['current_length']:<15}")
    print(f"{'Dialogue/Direction Ratio':<30} {before_analysis['dialogue_to_direction_ratio']:<15.2f} {after_analysis['dialogue_to_direction_ratio']:<15.2f}")
    print(f"{'Stage Direction Lines':<30} {before_analysis['structure']['stage_direction_lines']:<15} {after_analysis['structure']['stage_direction_lines']:<15}")
    print(f"{'Technical Cues':<30} {before_analysis['structure']['technical_cues']:<15} {after_analysis['structure']['technical_cues']:<15}")
    
    print("\n\nEnhancement Effectiveness:")
    if after_analysis['length_deficit'] == 0:
        print("✓ Target length achieved!")
    else:
        progress = (before_analysis['length_deficit'] - after_analysis['length_deficit']) / before_analysis['length_deficit'] * 100
        print(f"Length deficit reduced by {progress:.1f}%")


if __name__ == "__main__":
    print("=== SCENE DETAIL ENHANCEMENT SYSTEM DEMO ===\n")
    print("This system expands theatrical scenes with rich detail")
    print("to meet length requirements while maintaining quality.\n")
    
    # Run all demonstrations
    demonstrate_enhancement_strategies()
    demonstrate_detail_planning()
    demonstrate_scene_enhancement()
    demonstrate_specific_enhancements()
    demonstrate_prompt_generation()
    demonstrate_length_targeting()
    analyze_enhancement_quality()
    
    print("\n\n=== Demo Complete ===")
    print("\nKey Features Demonstrated:")
    print("- Scene analysis and length deficit calculation")
    print("- Strategic enhancement planning by priority")
    print("- Multiple enhancement strategies (subtext, atmosphere, etc.)")
    print("- Template-based enhancement for testing")
    print("- Enhanced prompt generation for LLM integration")
    print("- Targeting specific scene lengths")
    print("- Quality metrics tracking")
    
    print("\nNote: In production, template enhancements would be")
    print("replaced with LLM-generated content using the enhanced prompts.")