"""
Run management system for organizing and tracking play generation runs.
"""

from pathlib import Path
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
import shutil

logger = logging.getLogger(__name__)

class RunManager:
    """Manages play generation runs and their artifacts."""
    
    def __init__(self, base_dir: str = "runs") -> None:
        """Initialize run manager."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_run_id: Optional[str] = None
        self.current_run_dir: Optional[Path] = None
        self._load_index()
    
    def _load_index(self):
        """Load or create the run index."""
        self.index_file = self.base_dir / "index.json"
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                self.index = json.load(f)
        else:
            self.index = {"runs": {}}
            self._save_index()
    
    def _save_index(self):
        """Save the run index."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)
    
    def start_run(self, run_id: str) -> None:
        """Start a new run."""
        self.current_run_id = run_id
        self.current_run_dir = self.base_dir / run_id
        self.current_run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save run metadata
        metadata = {
            "run_id": run_id,
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
        self._save_metadata(metadata)
        
        # Update index
        self.index["runs"][run_id] = {
            "created_at": metadata["start_time"],
            "status": metadata["status"],
            "path": str(self.current_run_dir)
        }
        self._save_index()
        
        logger.info(f"Created new run: {run_id}")
    
    def end_run(self, status: str = "completed") -> None:
        """End the current run."""
        if not self.current_run_id or not self.current_run_dir:
            return
            
        # Update run metadata
        metadata = self._load_metadata()
        if metadata:
            metadata["end_time"] = datetime.now().isoformat()
            metadata["status"] = status
            self._save_metadata(metadata)
            
        # Reset current run state
        self.current_run_id = None
        self.current_run_dir = None
        
        # Update index
        self.index["runs"][metadata["run_id"]]["status"] = status
        self._save_index()
        
        logger.info(f"Updated run {metadata['run_id']} status to {status}")
    
    def save_artifact(self, run_id: str, name: str, data: Any) -> None:
        """Save an artifact to a specific run."""
        run_dir = self.get_run_dir(run_id)
        artifact_dir = run_dir / "artifacts"
        artifact_dir.mkdir(exist_ok=True)
        
        artifact_path = artifact_dir / f"{name}.json"
        with open(artifact_path, "w") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved artifact {name} for run {run_id}")
    
    def load_artifact(self, name: str) -> Optional[Dict[str, Any]]:
        """Load an artifact from the current run."""
        if not self.current_run_dir:
            return None
        
        artifact_path = self.current_run_dir / f"{name}.json"
        if not artifact_path.exists():
            return None
        
        with open(artifact_path, "r") as f:
            return json.load(f)
            
    def list_runs(self) -> List[Dict[str, Any]]:
        """List all runs."""
        runs = []
        
        for run_dir in self.base_dir.iterdir():
            if not run_dir.is_dir():
                continue
                
            metadata_path = run_dir / "metadata.json"
            if not metadata_path.exists():
                continue
                
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                runs.append(metadata)
                
        return sorted(runs, key=lambda x: x.get("start_time", ""), reverse=True)
        
    def get_run_metadata(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific run."""
        run_dir = self.base_dir / run_id
        metadata_path = run_dir / "metadata.json"
        
        if not metadata_path.exists():
            return None
            
        with open(metadata_path, "r") as f:
            return json.load(f)
            
    def delete_run(self, run_id: str) -> None:
        """Delete a run."""
        run_dir = self.base_dir / run_id
        if run_dir.exists():
            shutil.rmtree(run_dir)
            
    def cleanup_old_runs(self, max_age_days: int = 30) -> None:
        """Clean up old runs."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        for run_dir in self.base_dir.iterdir():
            if not run_dir.is_dir():
                continue
                
            metadata_path = run_dir / "metadata.json"
            if not metadata_path.exists():
                continue
                
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                
            start_time = datetime.fromisoformat(metadata.get("start_time", ""))
            if start_time < cutoff:
                self.delete_run(run_dir.name)
                
    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save run metadata."""
        if not self.current_run_dir:
            return
        
        metadata_path = self.current_run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> Optional[Dict[str, Any]]:
        """Load run metadata."""
        if not self.current_run_dir:
            return None
        
        metadata_path = self.current_run_dir / "metadata.json"
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, "r") as f:
            return json.load(f)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the run manager state."""
        return {
            "base_dir": str(self.base_dir),
            "current_run_id": self.current_run_id,
            "current_run_dir": str(self.current_run_dir) if self.current_run_dir else None
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the run manager state."""
        self.base_dir = Path(state.get("base_dir", self.base_dir))
        self.current_run_id = state.get("current_run_id")
        current_run_dir = state.get("current_run_dir")
        self.current_run_dir = Path(current_run_dir) if current_run_dir else None
    
    def get_run_dir(self, run_id: str) -> Path:
        """Get the directory for a specific run."""
        if run_id not in self.index["runs"]:
            raise ValueError(f"Run {run_id} not found")
        return Path(self.index["runs"][run_id]["path"])
    
    def update_run_status(self, run_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Update the status of a run."""
        run_dir = self.get_run_dir(run_id)
        metadata_file = run_dir / "metadata.json"
        
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        metadata["status"] = status
        metadata["updated_at"] = datetime.now().isoformat()
        if details:
            metadata.update(details)
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.index["runs"][run_id]["status"] = status
        self._save_index()
        
        logger.info(f"Updated run {run_id} status to {status}")
    
    def save_act_plan(self, run_id: str, act_number: int, plan: Dict[str, Any]):
        """Save an act plan."""
        run_dir = self.get_run_dir(run_id)
        act_dir = run_dir / "acts" / f"act{act_number}"
        act_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(act_dir / f"plan_{timestamp}.json", "w") as f:
            json.dump(plan, f, indent=2)
        
        # Update metadata
        metadata_file = run_dir / "metadata.json"
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        metadata["acts"][str(act_number)] = {
            "status": "planned",
            "plan_timestamp": timestamp
        }
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved plan for Act {act_number} in run {run_id}")
    
    def save_scene(self, run_id: str, act_number: int, scene_number: int, 
                  scene_data: Dict[str, Any]):
        """Save a generated scene."""
        run_dir = self.get_run_dir(run_id)
        scene_dir = run_dir / "acts" / f"act{act_number}" / "scenes" / f"scene{scene_number}"
        scene_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(scene_dir / f"scene_{timestamp}.json", "w") as f:
            json.dump(scene_data, f, indent=2)
        
        logger.info(f"Saved Scene {scene_number} for Act {act_number} in run {run_id}")
    
    def save_error(self, run_id: str, error: Exception, context: Dict[str, Any] = None) -> None:
        """Save an error that occurred during the run."""
        try:
            # Get current metadata
            metadata = self.get_run_metadata(run_id)
            if not metadata:
                metadata = {"status": "failed", "errors": []}
            
            # Initialize errors list if it doesn't exist
            if "errors" not in metadata:
                metadata["errors"] = []
            
            # Create error data
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {}
            }
            
            # Add error to metadata
            metadata["errors"].append(error_data)
            
            # Update metadata
            self.save_artifact(run_id, "metadata", metadata)
            logger.error(f"Saved error for run {run_id}: {str(error)}")
            
        except Exception as e:
            logger.error(f"Failed to save error for run {run_id}: {str(e)}")
            raise
    
    def cleanup_run(self, run_id: str):
        """Clean up a run directory."""
        if run_id not in self.index["runs"]:
            raise ValueError(f"Run {run_id} not found")
        
        run_dir = self.get_run_dir(run_id)
        try:
            shutil.rmtree(run_dir)
            del self.index["runs"][run_id]
            self._save_index()
            logger.info(f"Cleaned up run {run_id}")
        except Exception as e:
            logger.error(f"Failed to clean up run {run_id}: {str(e)}")
            raise 