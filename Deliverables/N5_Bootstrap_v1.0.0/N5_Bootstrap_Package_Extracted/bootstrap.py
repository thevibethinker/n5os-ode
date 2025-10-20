#!/usr/bin/env python3
"""
N5 OS Bootstrap Installer
Installs N5 operating system into a Zo Computer workspace
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")

def print_step(msg: str):
    print(f"{Colors.CYAN}▸ {msg}{Colors.END}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


class N5Bootstrapper:
    """Handles N5 installation"""
    
    def __init__(self):
        self.package_root = Path(__file__).parent
        self.target_root = Path("/home/workspace")
        self.n5_target = self.target_root / "N5"
        self.knowledge_target = self.target_root / "Knowledge"
        self.docs_target = self.target_root / "Documents"
        
        self.stats = {
            "files_copied": 0,
            "dirs_created": 0,
            "errors": 0
        }
    
    def verify_environment(self) -> bool:
        """Verify we're in a Zo workspace"""
        print_step("Verifying environment...")
        
        # Check if we're in Zo
        if not self.target_root.exists():
            print_error(f"Target directory {self.target_root} not found")
            print_error("Are you running this in a Zo Computer workspace?")
            return False
        
        # Check Python version
        if sys.version_info < (3, 10):
            print_error(f"Python 3.10+ required, found {sys.version}")
            return False
        
        print_success(f"Environment OK (Python {sys.version_info.major}.{sys.version_info.minor})")
        return True
    
    def check_existing_installation(self) -> bool:
        """Check if N5 is already installed"""
        if self.n5_target.exists():
            print_warning(f"N5 directory already exists at {self.n5_target}")
            response = input(f"{Colors.YELLOW}Overwrite? This will DELETE existing N5/ directory! (yes/no): {Colors.END}")
            if response.lower() != "yes":
                print_error("Installation cancelled")
                return False
            print_warning("Removing existing installation...")
            shutil.rmtree(self.n5_target)
            print_success("Removed old installation")
        return True
    
    def copy_directory(self, source: str, target: Path) -> int:
        """Copy a directory and return file count"""
        source_path = self.package_root / source
        if not source_path.exists():
            print_warning(f"Source {source} not found, skipping")
            return 0
        
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, target, dirs_exist_ok=True)
        
        # Count files
        file_count = len(list(target.rglob('*')))
        return file_count
    
    def install_n5_core(self):
        """Install core N5 components"""
        print_step("Installing N5 core components...")
        
        components = [
            ("scripts", self.n5_target / "scripts"),
            ("config", self.n5_target / "config"),
            ("schemas", self.n5_target / "schemas"),
            ("prefs", self.n5_target / "prefs"),
            ("commands", self.n5_target / "commands"),
        ]
        
        for source, target in components:
            count = self.copy_directory(source, target)
            self.stats["files_copied"] += count
            print_success(f"Installed {source}/ ({count} items)")
    
    def install_knowledge_base(self):
        """Install knowledge base"""
        print_step("Installing knowledge base...")
        
        # Create Knowledge directory if doesn't exist
        self.knowledge_target.mkdir(exist_ok=True)
        
        # Copy architectural docs
        source = self.package_root / "knowledge" / "architectural"
        target = self.knowledge_target / "architectural"
        
        if source.exists():
            count = self.copy_directory("knowledge/architectural", target)
            self.stats["files_copied"] += count
            print_success(f"Installed Knowledge/architectural/ ({count} items)")
        else:
            print_warning("No knowledge base found in package")
    
    def create_data_directories(self):
        """Create empty data directories"""
        print_step("Creating data directories...")
        
        directories = [
            self.n5_target / "lists",
            self.n5_target / "records" / "meetings",
            self.n5_target / "intelligence",
            self.n5_target / "config" / "credentials",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep
            (directory / ".gitkeep").write_text("")
            self.stats["dirs_created"] += 1
        
        print_success(f"Created {len(directories)} data directories")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print_step("Installing Python dependencies...")
        print_warning("This may take a minute...")
        
        packages = [
            "anthropic",
            "openai",
            "aiohttp",
            "beautifulsoup4",
            "pyyaml",
            "jsonschema",
            "watchdog",
            "gitpython"
        ]
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "-q"] + packages,
                check=True,
                capture_output=True
            )
            print_success(f"Installed {len(packages)} Python packages")
        except subprocess.CalledProcessError as e:
            print_warning("Some dependencies failed to install")
            print_warning("You can install them manually later with: pip install -U [package]")
    
    def create_documents_index(self):
        """Create Documents/N5.md if it doesn't exist"""
        print_step("Setting up Documents/N5.md...")
        
        self.docs_target.mkdir(exist_ok=True)
        n5_doc = self.docs_target / "N5.md"
        
        if n5_doc.exists():
            print_warning("Documents/N5.md already exists, skipping")
            return
        
        content = """# N5 Operating System

**Version:** 1.0.0  
**Initialized:** {date}

## Quick Reference

- Commands: `file 'N5/commands/README.md'`
- Preferences: `file 'N5/prefs/prefs.md'`
- Architecture: `file 'Knowledge/architectural/architectural_principles.md'`

## Getting Started

Run your first command:
```
/init-state-session
```

Or add your first knowledge:
```
/knowledge-add
```

## System Components

- **Lists:** Track items across categories
- **Meetings:** Process and extract meeting intelligence
- **Knowledge:** Personal knowledge base
- **Intelligence:** Learned patterns and preferences

## Next Steps

1. Read `file 'INSTALLATION.md'` for post-installation setup
2. Configure preferences in `file 'N5/prefs/prefs.md'`
3. Explore commands in `N5/commands/`
4. Start using the system!

---

*Installed from N5 Bootstrap Package v1.0.0*
"""
        import datetime
        content = content.format(date=datetime.date.today().isoformat())
        
        n5_doc.write_text(content)
        print_success("Created Documents/N5.md")
    
    def print_summary(self):
        """Print installation summary"""
        print_header("INSTALLATION COMPLETE")
        
        print(f"{Colors.GREEN}✓ Files copied: {self.stats['files_copied']}{Colors.END}")
        print(f"{Colors.GREEN}✓ Directories created: {self.stats['dirs_created']}{Colors.END}")
        
        if self.stats['errors'] > 0:
            print(f"{Colors.YELLOW}⚠ Errors: {self.stats['errors']}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Installation Summary:{Colors.END}")
        print(f"  N5 Core:      {self.n5_target}")
        print(f"  Knowledge:    {self.knowledge_target}")
        print(f"  Documents:    {self.docs_target}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        print(f"  1. Read:  file 'INSTALLATION.md'")
        print(f"  2. Configure: file 'N5/prefs/prefs.md'")
        print(f"  3. Start using: /init-state-session")
        
        print(f"\n{Colors.CYAN}🚀 N5 OS is ready to use!{Colors.END}\n")
    
    def run(self):
        """Execute bootstrap installation"""
        print_header("N5 OS BOOTSTRAP INSTALLER")
        print(f"{Colors.BOLD}Package:{Colors.END} {self.package_root}")
        print(f"{Colors.BOLD}Target:{Colors.END}  {self.target_root}")
        
        # Verification
        if not self.verify_environment():
            sys.exit(1)
        
        if not self.check_existing_installation():
            sys.exit(1)
        
        # Confirm installation
        print(f"\n{Colors.YELLOW}This will install N5 OS to {self.target_root}{Colors.END}")
        response = input(f"{Colors.BOLD}Continue? (yes/no): {Colors.END}")
        if response.lower() != "yes":
            print_error("Installation cancelled")
            sys.exit(0)
        
        # Execute installation steps
        try:
            self.install_n5_core()
            self.install_knowledge_base()
            self.create_data_directories()
            self.install_dependencies()
            self.create_documents_index()
            
            self.print_summary()
            
        except Exception as e:
            print_error(f"Installation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    bootstrapper = N5Bootstrapper()
    bootstrapper.run()
