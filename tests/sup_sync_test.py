from pathlib import Path
from typer.testing import CliRunner
from sup.main import app
import yaml
import pytest
from sup.config.sync import SyncConfig

runner = CliRunner()

def test_create_sync_with_instances(tmp_path):
    sync_folder = tmp_path / "test_sync"
    result = runner.invoke(
        app,
        [
            "sync",
            "create",
            str(sync_folder),
            "--source", "prod_instance",
            "--targets", "staging_instance,dev_workspace",
        ],
    )
    
    assert result.exit_code == 0
    assert sync_folder.exists()
    config_path = sync_folder / "sync_config.yml"
    assert config_path.exists()
    
    config = SyncConfig.from_yaml(config_path)
    assert config.source.instance == "prod_instance"
    assert config.source.workspace_id is None
    
    assert len(config.targets) == 2
    t1 = config.targets[0]
    t2 = config.targets[1]
    
    assert t1.instance == "staging_instance"
    assert t2.instance == "dev_workspace"

def test_create_sync_with_mixed_ids_and_instances(tmp_path):
    sync_folder = tmp_path / "mixed_sync"
    result = runner.invoke(
        app,
        [
            "sync",
            "create",
            str(sync_folder),
            "--source", "123",
            "--targets", "456,staging_instance",
        ],
    )
    
    assert result.exit_code == 0
    
    config = SyncConfig.from_yaml(sync_folder / "sync_config.yml")
    assert config.source.workspace_id == 123
    assert config.source.instance is None
    
    assert len(config.targets) == 2
    assert config.targets[0].workspace_id == 456
    assert config.targets[1].instance == "staging_instance"

def test_run_sync_dry_run_with_instances(tmp_path):
    # Create a sync folder first using the CLI to ensure structure is correct
    sync_folder = tmp_path / "run_sync"
    runner.invoke(
        app,
        [
            "sync",
            "create",
            str(sync_folder),
            "--source", "source_instance",
            "--targets", "target_instance",
        ],
    )

    # Execute dry run
    result = runner.invoke(
        app,
        ["sync", "run", str(sync_folder), "--dry-run"],
    )
    
    assert result.exit_code == 0
    # Check output for instance names
    assert "Pulling from Instance: source_instance" in result.output
    assert "Pushing to Instance: target_instance" in result.output
