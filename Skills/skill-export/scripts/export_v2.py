#!/usr/bin/env python3
"""
Skill Export Pipeline v2.0

Creates distributable versions of skills with proper separation:
- Source: Skills/<skill> (your working version, untouched)
- Export: Projects/zo-<skill> (distributable version)
- GitHub: vrijenattawar/zo-<skill> (public repo)

Key features:
- Never modifies source skill
- Generates bootloader for respectful installation
- Creates config templates from hardcoded values
- Scaffolds webhook support when applicable
- Pushes to GitHub with proper README

Usage:
    python3 export_v2.py <skill-slug>                    # Full export
    python3 export_v2.py <skill-slug> --dry-run         # Preview only
    python3 export_v2.py <skill-slug> --no-github       # Skip GitHub push
    python3 export_v2.py <skill-slug> --analyze-only    # Just show what would be extracted
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ExportConfig:
    """Configuration for skill export."""
    skill_slug: str
    source_dir: Path
    export_dir: Path
    github_repo: str
    dry_run: bool = False
    push_github: bool = True
    generate_bootloader: bool = True
    generate_webhook: bool = False
    
    @classmethod
    def from_skill(cls, skill_slug: str, dry_run: bool = False, push_github: bool = True):
        source_dir = Path("/home/workspace/Skills") / skill_slug
        if not source_dir.exists():
            raise FileNotFoundError(f"Skill not found: {source_dir}")
        
        export_dir = Path("/home/workspace/Projects") / f"zo-{skill_slug}"
        github_repo = f"zo-{skill_slug}"
        
        return cls(
            skill_slug=skill_slug,
            source_dir=source_dir,
            export_dir=export_dir,
            github_repo=github_repo,
            dry_run=dry_run,
            push_github=push_github
        )


@dataclass 
class ExtractedConfig:
    """Configuration values extracted from source for templating."""
    paths: dict = field(default_factory=dict)
    secrets: list = field(default_factory=list)
    webhooks: list = field(default_factory=list)
    integrations: dict = field(default_factory=dict)
    hardcoded_values: dict = field(default_factory=dict)


class SkillAnalyzer:
    """Analyzes source skill to understand what needs templating."""
    
    PATH_PATTERNS = [
        (r'/home/workspace/([A-Za-z0-9_/-]+)', 'workspace_path'),
        (r'Personal/([A-Za-z0-9_/-]+)', 'personal_path'),
        (r'N5/([A-Za-z0-9_/-]+)', 'n5_path'),
    ]
    
    SECRET_PATTERNS = [
        (r'os\.environ\.get\(["\']([A-Z_]+)["\']', 'env_var'),
        (r'os\.environ\[["\']([A-Z_]+)["\']', 'env_var'),
        (r'process\.env\.([A-Z_]+)', 'env_var'),
        (r'([A-Z_]+)_SECRET', 'secret_name'),
        (r'([A-Z_]+)_API_KEY', 'api_key'),
    ]
    
    WEBHOOK_INDICATORS = [
        'webhook', 'http.server', 'HTTPServer', 'BaseHTTPRequestHandler',
        'flask', 'fastapi', '/ingest', '/receive'
    ]
    
    INTEGRATION_PATTERNS = [
        (r'google_drive|use_app_google_drive', 'google_drive'),
        (r'google_calendar|use_app_google_calendar', 'google_calendar'),
        (r'airtable|use_app_airtable', 'airtable'),
        (r'gmail|use_app_gmail', 'gmail'),
        (r'notion|use_app_notion', 'notion'),
    ]
    
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.extracted = ExtractedConfig()
    
    def analyze(self) -> ExtractedConfig:
        """Analyze all files in the skill."""
        for file_path in self._get_text_files():
            self._analyze_file(file_path)
        return self.extracted
    
    def _get_text_files(self):
        text_extensions = {'.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh'}
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                path = Path(root) / file
                if path.suffix.lower() in text_extensions:
                    yield path
    
    def _analyze_file(self, file_path: Path):
        try:
            content = file_path.read_text()
        except Exception:
            return
        
        for pattern, category in self.PATH_PATTERNS:
            for match in re.finditer(pattern, content):
                full_path = match.group(0)
                if full_path not in self.extracted.paths:
                    self.extracted.paths[full_path] = {
                        'category': category,
                        'found_in': str(file_path.relative_to(self.source_dir))
                    }
        
        for pattern, category in self.SECRET_PATTERNS:
            for match in re.finditer(pattern, content):
                var_name = match.group(1)
                if var_name not in self.extracted.secrets:
                    self.extracted.secrets.append(var_name)
        
        content_lower = content.lower()
        for indicator in self.WEBHOOK_INDICATORS:
            if indicator.lower() in content_lower:
                self.extracted.webhooks.append({
                    'indicator': indicator,
                    'file': str(file_path.relative_to(self.source_dir))
                })
                break
        
        for pattern, integration in self.INTEGRATION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                if integration not in self.extracted.integrations:
                    self.extracted.integrations[integration] = []
                self.extracted.integrations[integration].append(
                    str(file_path.relative_to(self.source_dir))
                )


class Sanitizer:
    """Sanitizes skill content for distribution."""
    
    SANITIZE_PATTERNS = [
        (r'/home/workspace/', './'),
        (r'/home/\.z/[^/\s]*/([/\s"\')]|$)', r'./\1'),
        (r"N5/scripts/", "scripts/"),
        (r"N5/config/", "config/"),
        (r"N5/", ""),
        (r"file 'N5/[^']*'", "file 'config/settings.yaml'"),
        (r'sk-[A-Za-z0-9]{48,}', '<YOUR_OPENAI_API_KEY>'),
        (r'FILLOUT_SECRET_[A-Z0-9_]*', '<YOUR_FILLOUT_SECRET>'),
        (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '<YOUR_EMAIL>'),
        (r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', '<YOUR_PHONE>'),
        (r'https://[^/]*\.zo\.computer/[^\s\'\"]*', '<YOUR_WEBHOOK_URL>'),
        (r'va\.zo\.computer', '<YOUR_DOMAIN>'),
        (r"author: va\.zo\.computer", "author: <YOUR_HANDLE>"),
        (r'@vrijenattawar', '@<YOUR_GITHUB>'),
    ]
    
    def sanitize_content(self, content: str) -> str:
        for pattern, replacement in self.SANITIZE_PATTERNS:
            content = re.sub(pattern, replacement, content)
        return content
    
    def sanitize_file(self, source: Path, dest: Path):
        text_extensions = {'.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh', '.txt'}
        
        if source.suffix.lower() in text_extensions:
            try:
                content = source.read_text()
                sanitized = self.sanitize_content(content)
                dest.write_text(sanitized)
            except Exception as e:
                print(f"  Warning: Could not sanitize {source}: {e}")
                shutil.copy2(source, dest)
        else:
            shutil.copy2(source, dest)


class BootloaderGenerator:
    """Generates bootloader.py from template."""
    
    TEMPLATE_PATH = Path(__file__).parent.parent / "assets" / "bootloader_template.py"
    
    def generate(self, skill_slug: str, skill_description: str, 
                 analysis: ExtractedConfig) -> str:
        """Generate bootloader.py content from template."""
        template = self.TEMPLATE_PATH.read_text()
        
        required_paths = {}
        for path, info in analysis.paths.items():
            key = path.replace("/home/workspace/", "").replace("/", "_").replace(".", "_").replace("-", "_")
            if key and len(key) < 50:
                required_paths[key] = {
                    "default": path.replace("/home/workspace/", ""),
                    "description": f"Found in {info['found_in']}"
                }
        
        content = template
        content = content.replace("__SKILL_NAME_TITLE__", skill_slug.replace("-", " ").title())
        content = content.replace("__SKILL_SLUG__", skill_slug)
        content = content.replace("__SKILL_DESCRIPTION__", skill_description[:500] if skill_description else "")
        content = content.replace("__REQUIRED_PATHS__", json.dumps(required_paths, indent=4))
        content = content.replace("__REQUIRED_SECRETS__", json.dumps(analysis.secrets, indent=4))
        content = content.replace("__REQUIRED_INTEGRATIONS__", json.dumps(list(analysis.integrations.keys()), indent=4))
        
        return content


class ConfigGenerator:
    """Generates config templates from extracted values."""
    
    def generate_settings_template(self, skill_slug: str, analysis: ExtractedConfig) -> str:
        config = {
            "skill": {"name": skill_slug, "version": "1.0.0"},
            "paths": {},
            "integrations": {}
        }
        
        for path, info in analysis.paths.items():
            key = info['category'].replace('_path', '')
            clean_path = path.replace("/home/workspace/", "")
            if key not in config["paths"]:
                config["paths"][key] = clean_path
        
        for integration in analysis.integrations:
            config["integrations"][integration] = {
                "enabled": True,
                "config": "# Add integration-specific config here"
            }
        
        lines = [
            f"# {skill_slug} Settings",
            "# Copy this to settings.yaml and customize",
            "",
            yaml.dump(config, default_flow_style=False, sort_keys=False)
        ]
        return "\n".join(lines)
    
    def generate_webhook_template(self) -> str:
        return """# Webhook Configuration
# Copy this to webhook.yaml and customize

webhook:
  port: 8900
  secret: null  # Set via WEBHOOK_SECRET env var
  
  sources:
    otter:
      enabled: true
    fireflies:
      enabled: true
    generic:
      enabled: true

  auto_process: true
  save_raw: true
"""


class ReadmeGenerator:
    """Generates README.md for the exported skill."""
    
    def generate(self, skill_slug: str, skill_md_content: str, 
                 analysis: ExtractedConfig, has_webhook: bool) -> str:
        description = ""
        if "description:" in skill_md_content:
            match = re.search(r'description:\s*(.+?)(?:\n[a-z]+:|$)', skill_md_content, re.DOTALL)
            if match:
                description = match.group(1).strip()
        
        sections = [
            f"# {skill_slug.replace('-', ' ').title()}",
            "",
            description or "A Zo Computer skill.",
            "",
            "## Installation",
            "",
            "```bash",
            "cd /home/workspace/Skills",
            f"git clone https://github.com/vrijenattawar/zo-{skill_slug}.git {skill_slug}",
            f"python3 {skill_slug}/bootloader.py",
            "```",
            "",
            "The bootloader will:",
            "1. Survey your environment",
            "2. Detect potential conflicts", 
            "3. Propose an installation plan",
            "4. Execute only with your approval",
            "",
        ]
        
        if analysis.secrets:
            sections.extend([
                "## Required Secrets",
                "",
                "Set these in **Zo Settings > Developers**:",
                "",
            ])
            for secret in analysis.secrets:
                sections.append(f"- `{secret}`")
            sections.append("")
        
        if analysis.integrations:
            sections.extend([
                "## Required Integrations",
                "",
                "Connect these in **Zo Settings > Integrations**:",
                "",
            ])
            for integration in analysis.integrations:
                sections.append(f"- {integration.replace('_', ' ').title()}")
            sections.append("")
        
        if has_webhook:
            sections.extend([
                "## Webhook Ingestion",
                "",
                "This skill supports receiving data via webhooks.",
                "",
                "```bash",
                "python3 scripts/webhook_setup.py --register",
                "```",
                "",
            ])
        
        sections.extend([
            "## Configuration",
            "",
            "```bash",
            "cp config/settings.yaml.example config/settings.yaml",
            "```",
            "",
            "## License",
            "",
            "MIT",
            "",
            "---",
            "",
            "Built for [Zo Computer](https://zo.computer).",
        ])
        
        return "\n".join(sections)


class SkillExporterV2:
    """Main orchestrator for skill export v2."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.analyzer = SkillAnalyzer(config.source_dir)
        self.sanitizer = Sanitizer()
        self.analysis: Optional[ExtractedConfig] = None
    
    def analyze(self) -> ExtractedConfig:
        print(f"\n🔍 Analyzing {self.config.skill_slug}...")
        self.analysis = self.analyzer.analyze()
        
        print(f"   Found {len(self.analysis.paths)} configurable paths")
        print(f"   Found {len(self.analysis.secrets)} secrets/env vars")
        print(f"   Found {len(self.analysis.integrations)} integrations")
        print(f"   Webhook indicators: {len(self.analysis.webhooks) > 0}")
        
        self.config.generate_webhook = len(self.analysis.webhooks) > 0
        return self.analysis
    
    def export(self) -> dict:
        if not self.analysis:
            self.analyze()
        
        print(f"\n📦 Exporting to {self.config.export_dir}...")
        
        if self.config.dry_run:
            print("   [DRY RUN] Would create export directory")
            return {"status": "dry_run", "export_dir": str(self.config.export_dir)}
        
        if self.config.export_dir.exists():
            backup = self.config.export_dir.with_suffix(
                f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.move(self.config.export_dir, backup)
            print(f"   Backed up existing to {backup.name}")
        
        self.config.export_dir.mkdir(parents=True, exist_ok=True)
        
        print("   Sanitizing and copying files...")
        self._copy_and_sanitize()
        
        print("   Generating bootloader...")
        self._generate_bootloader()
        
        print("   Generating config templates...")
        self._generate_configs()
        
        print("   Generating README...")
        self._generate_readme()
        
        self._generate_gitignore()
        
        if self.config.push_github:
            print(f"\n🚀 Pushing to GitHub...")
            self._push_to_github()
        
        return {
            "status": "success",
            "export_dir": str(self.config.export_dir),
            "github_repo": f"https://github.com/vrijenattawar/{self.config.github_repo}" if self.config.push_github else None
        }
    
    def _copy_and_sanitize(self):
        for item in self.config.source_dir.rglob("*"):
            if item.is_file():
                if any(skip in str(item) for skip in ["__pycache__", ".git", ".pyc"]):
                    continue
                
                rel_path = item.relative_to(self.config.source_dir)
                dest = self.config.export_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                self.sanitizer.sanitize_file(item, dest)
    
    def _generate_bootloader(self):
        skill_md = self.config.source_dir / "SKILL.md"
        skill_content = skill_md.read_text() if skill_md.exists() else ""
        
        description = ""
        if "description:" in skill_content:
            match = re.search(r'description:\s*(.+?)(?:\n[a-z]+:|---)', skill_content, re.DOTALL)
            if match:
                description = match.group(1).strip()
        
        generator = BootloaderGenerator()
        content = generator.generate(self.config.skill_slug, description, self.analysis)
        (self.config.export_dir / "bootloader.py").write_text(content)
    
    def _generate_configs(self):
        config_dir = self.config.export_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        generator = ConfigGenerator()
        settings = generator.generate_settings_template(self.config.skill_slug, self.analysis)
        (config_dir / "settings.yaml.example").write_text(settings)
        
        if self.config.generate_webhook:
            webhook = generator.generate_webhook_template()
            (config_dir / "webhook.yaml.example").write_text(webhook)
    
    def _generate_readme(self):
        skill_md = self.config.source_dir / "SKILL.md"
        skill_content = skill_md.read_text() if skill_md.exists() else ""
        
        generator = ReadmeGenerator()
        readme = generator.generate(
            self.config.skill_slug,
            skill_content,
            self.analysis,
            self.config.generate_webhook
        )
        (self.config.export_dir / "README.md").write_text(readme)
    
    def _generate_gitignore(self):
        gitignore = """# Python
__pycache__/
*.py[cod]
*.so
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store

# Local config
config/settings.yaml
config/webhook.yaml
config/blocks.yaml
!config/*.example

# Logs
*.log

# Installation records
.installation_record.json
"""
        (self.config.export_dir / ".gitignore").write_text(gitignore)
    
    def _push_to_github(self):
        cwd = self.config.export_dir
        
        result = subprocess.run(
            ["gh", "repo", "view", f"vrijenattawar/{self.config.github_repo}"],
            capture_output=True, cwd=cwd
        )
        repo_exists = result.returncode == 0
        
        subprocess.run(["git", "init"], cwd=cwd, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=cwd, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Export {self.config.skill_slug} skill"],
            cwd=cwd, capture_output=True
        )
        
        if repo_exists:
            subprocess.run(
                ["git", "remote", "add", "origin", 
                 f"https://github.com/vrijenattawar/{self.config.github_repo}.git"],
                cwd=cwd, capture_output=True
            )
            result = subprocess.run(
                ["git", "push", "-f", "origin", "main"],
                cwd=cwd, capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"   ✓ Updated https://github.com/vrijenattawar/{self.config.github_repo}")
            else:
                print(f"   ⚠ Push failed: {result.stderr}")
        else:
            result = subprocess.run(
                ["gh", "repo", "create", self.config.github_repo,
                 "--public",
                 "--description", f"Zo Computer skill: {self.config.skill_slug}",
                 "--source", str(cwd),
                 "--push"],
                cwd=cwd, capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"   ✓ Created https://github.com/vrijenattawar/{self.config.github_repo}")
            else:
                print(f"   ⚠ GitHub push failed: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(
        description="Export skills with proper separation (source → export → GitHub)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 export_v2.py meeting-ingestion              # Full export + GitHub
  python3 export_v2.py pulse --dry-run                # Preview only
  python3 export_v2.py thread-close --no-github       # Export without GitHub
  python3 export_v2.py survey-dashboard --analyze-only  # Just analyze
        """
    )
    
    parser.add_argument("skill_slug", help="Skill to export (e.g., 'meeting-ingestion')")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--no-github", action="store_true", help="Skip GitHub push")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't export")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        config = ExportConfig.from_skill(
            args.skill_slug,
            dry_run=args.dry_run,
            push_github=not args.no_github
        )
        
        exporter = SkillExporterV2(config)
        analysis = exporter.analyze()
        
        if args.analyze_only:
            if args.json:
                print(json.dumps({
                    "paths": analysis.paths,
                    "secrets": analysis.secrets,
                    "webhooks": analysis.webhooks,
                    "integrations": analysis.integrations
                }, indent=2))
            else:
                print("\n📊 ANALYSIS RESULTS")
                print("=" * 60)
                print(f"\nConfigurable Paths ({len(analysis.paths)}):")
                for path in list(analysis.paths.keys())[:10]:
                    print(f"   • {path}")
                if len(analysis.paths) > 10:
                    print(f"   ... and {len(analysis.paths) - 10} more")
                print(f"\nSecrets/Env Vars ({len(analysis.secrets)}):")
                for secret in analysis.secrets:
                    print(f"   • {secret}")
                print(f"\nIntegrations ({len(analysis.integrations)}):")
                for integration in analysis.integrations:
                    print(f"   • {integration}")
                print(f"\nWebhook Support: {'Yes' if analysis.webhooks else 'No'}")
            return
        
        result = exporter.export()
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("✓ EXPORT COMPLETE")
            print("=" * 60)
            print(f"\nLocal: {result['export_dir']}")
            if result.get('github_repo'):
                print(f"GitHub: {result['github_repo']}")
            print(f"\nSource skill unchanged: {config.source_dir}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main() or 0)
