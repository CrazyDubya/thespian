"""
Checkpoint manager for saving and restoring production state.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class Checkpoint(BaseModel):
    """Represents a saved checkpoint of production state."""
    
    id: str = Field(..., description="Unique checkpoint identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    name: str = Field(..., description="Human readable checkpoint name")
    description: str = Field(default="", description="Optional description")
    data: Dict[str, Any] = Field(default_factory=dict, description="Checkpoint data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Checkpoint metadata")


class CheckpointManager:
    """Manages saving and loading of production checkpoints."""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized checkpoint manager with directory: {self.checkpoint_dir}")
    
    def save_checkpoint(self, checkpoint_id: str, name: str, data: Dict[str, Any], 
                       description: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a checkpoint.
        
        Args:
            checkpoint_id: Unique identifier for the checkpoint
            name: Human readable name
            data: Data to save
            description: Optional description
            metadata: Optional metadata
            
        Returns:
            Path to saved checkpoint file
        """
        checkpoint = Checkpoint(
            id=checkpoint_id,
            name=name,
            description=description,
            data=data,
            metadata=metadata or {}
        )
        
        filename = f"{checkpoint_id}.json"
        filepath = self.checkpoint_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.model_dump(), f, indent=2, default=str)
            
            logger.info(f"Saved checkpoint '{name}' to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint '{name}': {e}")
            raise
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Loaded checkpoint or None if not found
        """
        filename = f"{checkpoint_id}.json"
        filepath = self.checkpoint_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Checkpoint {checkpoint_id} not found at {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            checkpoint = Checkpoint(**data)
            logger.info(f"Loaded checkpoint '{checkpoint.name}' from {filepath}")
            return checkpoint
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None
    
    def list_checkpoints(self) -> List[Checkpoint]:
        """List all available checkpoints.
        
        Returns:
            List of checkpoint objects
        """
        checkpoints = []
        
        for filepath in self.checkpoint_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                checkpoint = Checkpoint(**data)
                checkpoints.append(checkpoint)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint from {filepath}: {e}")
        
        # Sort by timestamp, newest first
        checkpoints.sort(key=lambda x: x.timestamp, reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        filename = f"{checkpoint_id}.json"
        filepath = self.checkpoint_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return False
        
        try:
            filepath.unlink()
            logger.info(f"Deleted checkpoint {checkpoint_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            return False
    
    def cleanup_old_checkpoints(self, max_checkpoints: int = 10) -> int:
        """Clean up old checkpoints, keeping only the most recent ones.
        
        Args:
            max_checkpoints: Maximum number of checkpoints to keep
            
        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.list_checkpoints()
        
        if len(checkpoints) <= max_checkpoints:
            return 0
        
        to_delete = checkpoints[max_checkpoints:]
        deleted_count = 0
        
        for checkpoint in to_delete:
            if self.delete_checkpoint(checkpoint.id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old checkpoints")
        return deleted_count