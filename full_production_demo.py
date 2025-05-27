"""
Full production demo showcasing all enhancements working together.
"""

import sys
import os
sys.path.append('.')

from thespian.production import ProductionWorkflowManager, ProductionMetricsTracker
from thespian.config.enhanced_prompts import get_enhanced_scene_prompt
import json
from datetime import datetime
import argparse


def run_enhanced_production(
    premise: str,
    themes: list = None,
    num_acts: int = 2,
    scenes_per_act: int = 4,
    target_length: int = 5000,
    save_output: bool = True
):
    """Run a complete enhanced theatrical production.
    
    Args:
        premise: The story premise
        themes: List of themes to explore
        num_acts: Number of acts
        scenes_per_act: Scenes per act
        target_length: Target character count per scene
        save_output: Whether to save the output files
    """
    print("\n" + "🎭" * 30)
    print("ENHANCED THEATRICAL PRODUCTION SYSTEM")
    print("Featuring: Multi-Agent Collaboration | Scene Workshops | Detail Enhancement")
    print("🎭" * 30 + "\n")
    
    # Initialize workflow manager with all enhancements
    workflow_manager = ProductionWorkflowManager(
        target_scene_length=target_length,
        max_workshop_iterations=3,
        enable_all_enhancements=True,
        track_metrics=True
    )
    
    # Initialize separate metrics tracker for detailed analysis
    metrics_tracker = ProductionMetricsTracker()
    metrics_tracker.start_production(premise, num_acts, scenes_per_act)
    
    try:
        # Generate the production
        print(f"📋 Production Parameters:")
        print(f"   Premise: {premise[:100]}...")
        print(f"   Themes: {', '.join(themes or ['human condition'])}")
        print(f"   Structure: {num_acts} acts × {scenes_per_act} scenes = {num_acts * scenes_per_act} total scenes")
        print(f"   Target length: {target_length} characters per scene")
        print(f"   Total target: ~{target_length * num_acts * scenes_per_act:,} characters")
        print("\n" + "-" * 60 + "\n")
        
        # Run the enhanced production workflow
        result = workflow_manager.generate_enhanced_production(
            premise=premise,
            themes=themes or ["human nature", "transformation", "connection"],
            num_acts=num_acts,
            scenes_per_act=scenes_per_act,
            style="contemporary drama with psychological depth"
        )
        
        # Mark production complete
        metrics_tracker.end_production()
        
        # Save outputs if requested
        if save_output and result["status"] == "completed":
            save_production_outputs(result, metrics_tracker)
        
        # Print final statistics
        print_production_statistics(result)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Production failed: {e}")
        metrics_tracker.end_production()
        raise


def save_production_outputs(result: dict, metrics_tracker: ProductionMetricsTracker):
    """Save all production outputs to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output/production_{timestamp}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n💾 Saving production to: {output_dir}/")
    
    # Save the complete script
    script_path = os.path.join(output_dir, "complete_script.txt")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(result["production"]["script"])
    print(f"   ✓ Script saved: {script_path}")
    
    # Save production metadata
    metadata_path = os.path.join(output_dir, "production_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(result["production"]["metadata"], f, indent=2)
    print(f"   ✓ Metadata saved: {metadata_path}")
    
    # Save quality report
    quality_path = os.path.join(output_dir, "quality_report.json")
    with open(quality_path, 'w', encoding='utf-8') as f:
        json.dump(result["production"]["quality_report"], f, indent=2)
    print(f"   ✓ Quality report saved: {quality_path}")
    
    # Save workflow metrics
    workflow_path = os.path.join(output_dir, "workflow_metrics.json")
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metrics": result["metrics"],
            "workflow_stages": result["workflow_stages"]
        }, f, indent=2)
    print(f"   ✓ Workflow metrics saved: {workflow_path}")
    
    # Save detailed metrics from tracker
    detailed_metrics_path = os.path.join(output_dir, "detailed_metrics.json")
    metrics_tracker.save_metrics(detailed_metrics_path)
    print(f"   ✓ Detailed metrics saved: {detailed_metrics_path}")
    
    # Create a summary README
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(generate_production_readme(result))
    print(f"   ✓ README saved: {readme_path}")
    
    print(f"\n✅ All outputs saved to: {output_dir}/")


def generate_production_readme(result: dict) -> str:
    """Generate a README file for the production."""
    metadata = result["production"]["metadata"]
    metrics = result["metrics"]
    quality = result["production"]["quality_report"]
    
    readme = f"""# {metadata.get('title', 'Theatrical Production')}

Generated by the Enhanced Theatrical Production System

## Production Details

- **Premise**: {metadata.get('premise', 'N/A')}
- **Themes**: {', '.join(metadata.get('themes', []))}
- **Generated**: {metadata.get('generation_date', 'Unknown')}
- **Workflow Version**: {metadata.get('workflow_version', '1.0')}

## Statistics

### Length Metrics
- **Total Length**: {metrics['length_metrics']['total_length']:,} characters
- **Average Scene**: {metrics['length_metrics']['average_length']:,.0f} characters
- **Target Achievement**: {quality['average_scene_length'] / metrics['length_metrics']['target_length'] * 100:.1f}%

### Collaboration Metrics
- **Workshop Rounds**: {metrics['collaboration_metrics']['average_workshop_rounds']:.1f} per scene
- **Total Iterations**: {metrics['collaboration_metrics']['total_iterations']}
- **Agent Types**: {len(metrics['collaboration_metrics']['agent_contributions'])}

### Performance
- **Total Time**: {metrics['timing_metrics']['total_duration']}
- **Per Scene**: {metrics['timing_metrics']['average_scene_time']}

### Quality
- **Average Quality Score**: {quality['quality_scores']['average']:.2f}/1.0
- **Length Target Met**: {'✓' if quality['meets_length_targets'] else '✗'}
- **Workshop Effectiveness**: {quality['workshop_effectiveness']['average_iterations']:.1f} iterations average

## Files

- `complete_script.txt` - The full theatrical script
- `production_metadata.json` - Production metadata
- `quality_report.json` - Detailed quality metrics
- `workflow_metrics.json` - Workflow performance data
- `detailed_metrics.json` - Comprehensive metrics tracking

## Features Used

This production utilized:
- ✓ Enhanced agent collaboration
- ✓ Multi-round scene workshops
- ✓ Detail enhancement system
- ✓ Structured agent communication
- ✓ Comprehensive metrics tracking

---
Generated with the Enhanced Theatrical Production System
"""
    return readme


def print_production_statistics(result: dict):
    """Print detailed production statistics."""
    if result["status"] != "completed":
        print("\n⚠️  Production did not complete successfully.")
        return
    
    metrics = result["metrics"]
    quality = result["production"]["quality_report"]
    
    print("\n" + "=" * 60)
    print("📈 DETAILED PRODUCTION STATISTICS")
    print("=" * 60)
    
    # Scene breakdown
    print("\n📄 SCENE BREAKDOWN:")
    for stage in result["workflow_stages"]:
        if stage["name"].startswith("act_"):
            scene_name = stage["name"].replace("_", " ").title()
            duration = stage.get("duration", 0)
            print(f"   {scene_name}: {duration:.1f}s")
    
    # Length analysis
    lengths = metrics["length_metrics"]
    print(f"\n📏 LENGTH ANALYSIS:")
    print(f"   Total: {lengths['total_length']:,} characters")
    print(f"   Average: {lengths['average_length']:,.0f} chars/scene")
    print(f"   Min: {lengths['min_length']:,} chars")
    print(f"   Max: {lengths['max_length']:,} chars")
    print(f"   Target: {lengths['target_length']:,} chars")
    print(f"   Achievement: {lengths['average_length'] / lengths['target_length'] * 100:.1f}%")
    
    # Workshop effectiveness
    workshop = quality["workshop_effectiveness"]
    print(f"\n🔄 WORKSHOP EFFECTIVENESS:")
    print(f"   Total workshops: {workshop['total_workshops']}")
    print(f"   Average iterations: {workshop['average_iterations']:.2f}")
    
    # Agent participation
    agents = metrics["collaboration_metrics"]["agent_contributions"]
    if agents:
        print(f"\n🎭 AGENT PARTICIPATION:")
        for agent, count in sorted(agents.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {agent}: {count} contributions")
    
    # Time breakdown
    timing = metrics["timing_metrics"]
    print(f"\n⏱️  TIME BREAKDOWN:")
    print(f"   Total: {timing['total_duration']}")
    print(f"   Average per scene: {timing['average_scene_time']}")
    
    # Stage timing
    if timing["stage_durations"]:
        print(f"\n   Stage Durations:")
        for stage, duration in sorted(timing["stage_durations"].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {stage}: {duration:.2f}s")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point for the production demo."""
    parser = argparse.ArgumentParser(
        description="Run an enhanced theatrical production with all features"
    )
    parser.add_argument(
        "--premise",
        type=str,
        default="Two estranged siblings reunite at their childhood home to settle their deceased parent's estate, uncovering long-buried secrets that force them to confront their shared past and redefine their relationship.",
        help="The premise for the theatrical production"
    )
    parser.add_argument(
        "--themes",
        type=str,
        nargs="+",
        default=["family", "forgiveness", "memory", "identity"],
        help="Themes to explore in the production"
    )
    parser.add_argument(
        "--acts",
        type=int,
        default=2,
        help="Number of acts (default: 2)"
    )
    parser.add_argument(
        "--scenes-per-act",
        type=int,
        default=4,
        help="Scenes per act (default: 4)"
    )
    parser.add_argument(
        "--target-length",
        type=int,
        default=5000,
        help="Target character count per scene (default: 5000)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output files"
    )
    
    args = parser.parse_args()
    
    # Run the production
    try:
        result = run_enhanced_production(
            premise=args.premise,
            themes=args.themes,
            num_acts=args.acts,
            scenes_per_act=args.scenes_per_act,
            target_length=args.target_length,
            save_output=not args.no_save
        )
        
        if result["status"] == "completed":
            print("\n✨ Production completed successfully!")
            print(f"   Total length: {result['metrics']['length_metrics']['total_length']:,} characters")
            print(f"   Quality score: {result['production']['quality_report']['quality_scores']['average']:.2f}/1.0")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Production interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Production failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()