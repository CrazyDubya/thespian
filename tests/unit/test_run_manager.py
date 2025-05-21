import os
import shutil
import tempfile
import pytest
from thespian.llm.run_manager import RunManager

def test_run_manager_lifecycle():
    temp_dir = tempfile.mkdtemp()
    try:
        manager = RunManager(base_dir=temp_dir)
        run_id = "test_run_123"
        # Start a run
        manager.start_run(run_id)
        assert manager.current_run_id == run_id
        assert os.path.exists(os.path.join(temp_dir, run_id))
        # Save artifact
        data = {"foo": "bar"}
        manager.save_artifact(run_id, "test_artifact", data)
        artifact_path = os.path.join(temp_dir, run_id, "artifacts", "test_artifact.json")
        assert os.path.exists(artifact_path)
        # Get run metadata
        meta = manager.get_run_metadata(run_id)
        assert meta["run_id"] == run_id
        # End run
        manager.end_run(status="completed")
        meta2 = manager.get_run_metadata(run_id)
        assert meta2["status"] == "completed"
        # Delete run
        manager.delete_run(run_id)
        assert not os.path.exists(os.path.join(temp_dir, run_id))
    finally:
        shutil.rmtree(temp_dir)

def test_run_manager_missing_metadata():
    temp_dir = tempfile.mkdtemp()
    try:
        manager = RunManager(base_dir=temp_dir)
        # get_run_metadata should return None for missing run
        assert manager.get_run_metadata("no_such_run") is None
    finally:
        shutil.rmtree(temp_dir) 