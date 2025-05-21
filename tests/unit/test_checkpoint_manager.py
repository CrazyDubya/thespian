import os
import shutil
import tempfile
import time
from datetime import timedelta, datetime
from thespian.checkpoints.checkpoint_manager import CheckpointManager

def test_checkpoint_manager_lifecycle():
    temp_dir = tempfile.mkdtemp()
    try:
        manager = CheckpointManager(checkpoint_dir=temp_dir, checkpoint_ttl=timedelta(seconds=1))
        scene_id = "scene_abc123"
        data = {"foo": "bar", "timestamp": datetime.now().isoformat()}
        # Save checkpoint
        manager.save_checkpoint(scene_id, data)
        checkpoint_path = os.path.join(temp_dir, f"{scene_id}.json")
        assert os.path.exists(checkpoint_path)
        # Load checkpoint
        loaded = manager.load_checkpoint(scene_id)
        assert loaded["foo"] == "bar"
        # Cleanup checkpoint
        manager.cleanup_checkpoint(scene_id)
        assert not os.path.exists(checkpoint_path)
    finally:
        shutil.rmtree(temp_dir)

def test_checkpoint_manager_cleanup_old():
    temp_dir = tempfile.mkdtemp()
    try:
        manager = CheckpointManager(checkpoint_dir=temp_dir, checkpoint_ttl=timedelta(seconds=1))
        scene_id = "scene_old"
        data = {"foo": "old", "timestamp": (datetime.now() - timedelta(days=2)).isoformat()}
        manager.save_checkpoint(scene_id, data)
        checkpoint_path = os.path.join(temp_dir, f"{scene_id}.json")
        assert os.path.exists(checkpoint_path)
        # Manually set mtime to old
        old_time = time.time() - 60*60*24*2
        os.utime(checkpoint_path, (old_time, old_time))
        # Cleanup old checkpoints
        manager.cleanup_old_checkpoints()
        assert not os.path.exists(checkpoint_path)
    finally:
        shutil.rmtree(temp_dir) 