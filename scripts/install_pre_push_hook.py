"""
Install git pre-push hook for regression testing.

This script installs the appropriate pre-push hook based on the platform.
"""

import sys
import platform
import shutil
from pathlib import Path

# Configure UTF-8 encoding
try:
    import scripts.encoding_config
    ENCODING = scripts.encoding_config.UTF8
except ImportError:
    # Fallback if encoding_config not available
    ENCODING = "utf-8"


def install_hook():
    """Install the pre-push hook."""
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"
    hook_file = hooks_dir / "pre-push"
    
    if not hooks_dir.exists():
        print(f"Error: .git/hooks directory not found. Are you in a git repository?")
        sys.exit(1)
    
    # Determine which hook to use based on platform
    system = platform.system()
    
    if system == "Windows":
        source_hook = project_root / "scripts" / "pre-push-hook.ps1"
        # Read with explicit UTF-8 encoding
        hook_content = source_hook.read_text(encoding=ENCODING)
        # PowerShell hooks need a shebang
        hook_content = "#!" + sys.executable.replace("python.exe", "pwsh.exe") + "\n" + hook_content
    else:
        source_hook = project_root / "scripts" / "pre-push-hook.sh"
        # Read with explicit UTF-8 encoding
        hook_content = source_hook.read_text(encoding=ENCODING)
    
    # Write the hook with explicit UTF-8 encoding
    hook_file.write_text(hook_content, encoding=ENCODING)
    
    # Make executable on Unix-like systems
    if system != "Windows":
        import stat
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    
    print(f"✅ Pre-push hook installed at: {hook_file}")
    print(f"\nThe hook will prevent pushing if any previously passing test fails.")
    print(f"\nTo create a baseline, run:")
    print(f"  python scripts/regression_test.py update")


if __name__ == "__main__":
    install_hook()

