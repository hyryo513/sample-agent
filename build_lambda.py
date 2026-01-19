#!/usr/bin/env python3
"""Lambda deployment package builder for Strands-based agents.

This script orchestrates creation of AWS Lambda deployment packages (.zip files)
with bundled dependencies and lib1 shared library. Packages are created per-agent
and ready for direct AWS Lambda deployment.

Usage:
    python build_lambda.py agent-alpha [1.0.0]
    python build_lambda.py agent-beta [2.1.0]
"""
import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional


class LambdaPackageBuilder:
    """Build AWS Lambda deployment packages for Strands agents."""
    
    def __init__(self, workspace_root: Path, agent_name: str, version: Optional[str] = None):
        """Initialize builder.
        
        Args:
            workspace_root: Root of monorepo.
            agent_name: Agent package name (agent-alpha or agent-beta).
            version: Semantic version tag (e.g., 1.0.0). Uses workspace version if None.
        """
        self.workspace_root = workspace_root
        self.agent_name = agent_name
        self.agent_dir = workspace_root / "packages" / agent_name
        self.version = version or self._get_workspace_version()
        self.artifact_name = f"{agent_name}-v{self.version}"
    
    def _get_workspace_version(self) -> str:
        """Extract version from root pyproject.toml."""
        pyproject = self.workspace_root / "pyproject.toml"
        if not pyproject.exists():
            return "0.0.0"
        
        for line in pyproject.read_text().split('\n'):
            if line.startswith('version'):
                # Extract version value from: version = "X.Y.Z"
                return line.split('"')[1]
        return "0.0.0"
    
    def validate(self) -> bool:
        """Validate agent package exists and structure is correct."""
        if not self.agent_dir.exists():
            print(f"✗ Agent package not found: {self.agent_dir}")
            return False
        
        pyproject = self.agent_dir / "pyproject.toml"
        if not pyproject.exists():
            print(f"✗ pyproject.toml not found: {pyproject}")
            return False
        
        src_dir = self.agent_dir / "src"
        if not src_dir.exists():
            print(f"✗ src/ directory not found: {src_dir}")
            return False
        
        return True
    
    def build(self, output_dir: Optional[Path] = None) -> Path:
        """Build Lambda deployment package.
        
        Args:
            output_dir: Directory to write .zip file. Defaults to workspace root.
            
        Returns:
            Path to created .zip file.
        """
        output_dir = output_dir or self.workspace_root
        zip_path = output_dir / f"{self.artifact_name}.zip"
        
        with tempfile.TemporaryDirectory() as staging_dir:
            staging = Path(staging_dir)
            
            # Step 1: Install agent package and dependencies
            print(f"\n📦 Installing {self.agent_name} and dependencies...")
            self._install_dependencies(staging)
            
            # Step 2: Bundle lib1 shared library
            print("📦 Bundling lib1 shared library...")
            self._bundle_lib1(staging)
            
            # Step 3: Clean up unnecessary files
            print("🧹 Cleaning up unnecessary files...")
            self._cleanup_unnecessary_files(staging)
            
            # Step 4: Create zip archive
            print("🏗️  Creating Lambda deployment zip...")
            self._create_zip(staging, zip_path)
        
        return zip_path
    
    def _install_dependencies(self, staging: Path) -> None:
        """Install agent and dependencies into staging directory."""
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-t",
            str(staging),
            "-e",
            str(self.agent_dir),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Failed to install dependencies:")
            print(result.stderr)
            raise RuntimeError(f"pip install failed for {self.agent_name}")
    
    def _bundle_lib1(self, staging: Path) -> None:
        """Bundle lib1 shared library."""
        lib1_dir = self.workspace_root / "packages" / "lib1"
        
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-t",
            str(staging),
            "-e",
            str(lib1_dir),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Failed to install lib1:")
            print(result.stderr)
            raise RuntimeError("pip install failed for lib1")
    
    def _cleanup_unnecessary_files(self, staging: Path) -> None:
        """Remove unnecessary files to reduce package size."""
        # Remove pip, setuptools, wheel, and other build tools
        unwanted_dirs = [
            "*.dist-info",
            "*.egg-info",
            "pip*",
            "setuptools*",
            "wheel*",
            "pkg_resources*",
        ]
        
        for pattern in unwanted_dirs:
            for item in staging.glob(f"**/{pattern}"):
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
        
        # Remove __pycache__ and compiled Python files
        for pycache in staging.glob("**/__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)
        
        for pyc_file in staging.glob("**/*.pyc"):
            pyc_file.unlink()
        
        for pyo_file in staging.glob("**/*.pyo"):
            pyo_file.unlink()
    
    def _create_zip(self, staging: Path, zip_path: Path) -> None:
        """Create zip archive from staging directory."""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in staging.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(staging)
                    zf.write(file_path, arcname=arcname)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✓ Lambda package created: {zip_path.name} ({size_mb:.1f} MB)")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python build_lambda.py <agent-name> [version]")
        print("  agent-name: agent-alpha or agent-beta")
        print("  version: semantic version (optional, e.g., 1.0.0)")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    
    workspace_root = Path(__file__).parent
    
    builder = LambdaPackageBuilder(workspace_root, agent_name, version)
    
    print(f"🔨 Building Lambda package: {builder.artifact_name}")
    
    if not builder.validate():
        sys.exit(1)
    
    try:
        zip_path = builder.build()
        print(f"\n✅ Build successful: {zip_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
