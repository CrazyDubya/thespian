from typing import Dict, List, Optional
import os
import json

def extract_scenes_from_run(run_dir: str) -> Dict[str, Dict[str, str]]:
    """Extract scenes from a run directory."""
    scenes: Dict[str, Dict[str, str]] = {}
    acts_dir = os.path.join(run_dir, "acts")
    if not os.path.isdir(acts_dir):
        print(f"Acts directory not found: {acts_dir}")
        return scenes
    for act_name in sorted(os.listdir(acts_dir)):
        act_path = os.path.join(acts_dir, act_name)
        if not os.path.isdir(act_path):
            continue
        scenes_dir = os.path.join(act_path, "scenes")
        if not os.path.isdir(scenes_dir):
            continue
        for scene_name in sorted(os.listdir(scenes_dir)):
            scene_path = os.path.join(scenes_dir, scene_name)
            if not os.path.isdir(scene_path):
                continue
            # Find the most recent scene file
            scene_files = [f for f in os.listdir(scene_path) if f.endswith('.json')]
            if not scene_files:
                continue
            scene_files.sort(reverse=True)
            scene_file = scene_files[0]
            scene_file_path = os.path.join(scene_path, scene_file)
            try:
                with open(scene_file_path, 'r') as f:
                    data = json.load(f)
                    scene_text = data.get("scene", "")
                    scenes.setdefault(act_name, {})[scene_name] = scene_text
            except Exception as e:
                print(f"Error reading {scene_file_path}: {e}")
    return scenes

def consolidate_scenes(run_dir: str, output_file: Optional[str] = None) -> None:
    """Consolidate all scenes from a run into a single text file."""
    scenes = extract_scenes_from_run(run_dir)
    if not scenes:
        print("No scenes found.")
        return
    if output_file is None:
        output_file = os.path.join(run_dir, "consolidated_scenes.txt")
    with open(output_file, 'w') as out:
        for act_name in sorted(scenes.keys()):
            out.write(f"=== {act_name} ===\n")
            for scene_name in sorted(scenes[act_name].keys()):
                out.write(f"--- {scene_name} ---\n")
                out.write(scenes[act_name][scene_name])
                out.write("\n\n")
    print(f"Scenes consolidated into {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract_scenes.py <run_dir> [output_file]")
    else:
        run_dir = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        consolidate_scenes(run_dir, output_file) 