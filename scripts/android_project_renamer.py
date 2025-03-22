#!/usr/bin/env python3
import os
import re
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime

class AndroidProjectRenamer:
    def __init__(self, project_path, old_app_name, new_app_name, old_package, new_package, log_file=None):
        self.project_path = Path(project_path)
        self.old_app_name = old_app_name
        self.new_app_name = new_app_name
        self.old_package = old_package
        self.new_package = new_package
        
        # Convert package names to directory paths
        self.old_package_path = self.old_package.replace('.', '/')
        self.new_package_path = self.new_package.replace('.', '/')
        
        # Key directories
        self.app_dir = self.project_path / 'app'
        self.src_dir = self.app_dir / 'src'
        self.main_dir = self.src_dir / 'main'
        self.java_dir = self.main_dir / 'java'
        self.res_dir = self.main_dir / 'res'
        
        # Setup logging
        self.setup_logging(log_file)
        
        # Track changes
        self.changes = {
            'app_name': [],
            'gradle_files': [],
            'manifest_files': [],
            'source_files': []
        }
        
    def setup_logging(self, log_file=None):
        """Set up logging to console and optionally to a file"""
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"android_rename_{timestamp}.log"
            
        # Configure logging
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AndroidProjectRenamer')
        self.logger.info(f"Log file created at: {log_file}")
        self.logger.info(f"Starting Android project renaming process")
        self.logger.info(f"Project path: {self.project_path}")
        self.logger.info(f"App name: '{self.old_app_name}' -> '{self.new_app_name}'")
        self.logger.info(f"Package: {self.old_package} -> {self.new_package}")
        
    def rename_app_name(self):
        """Rename the app name in strings.xml"""
        self.logger.info("Starting app name renaming...")
        strings_xml = self.res_dir / 'values' / 'strings.xml'
        if strings_xml.exists():
            content = strings_xml.read_text(encoding='utf-8')
            original = content
            new_content = re.sub(
                r'<string name="app_name">.*?</string>',
                f'<string name="app_name">{self.new_app_name}</string>',
                content
            )
            
            if original != new_content:
                strings_xml.write_text(new_content, encoding='utf-8')
                self.logger.info(f"✓ Updated app name in {strings_xml}")
                self.changes['app_name'].append(str(strings_xml))
            else:
                self.logger.info(f"No changes needed in {strings_xml}")
        else:
            self.logger.warning(f"Warning: {strings_xml} not found!")
            
    def update_settings_gradle(self):
        """Update project name in settings.gradle files"""
        settings_gradle_kts = self.project_path / 'settings.gradle.kts'
        settings_gradle = self.project_path / 'settings.gradle'
        
        for settings_file in [settings_gradle_kts, settings_gradle]:
            if settings_file.exists():
                content = settings_file.read_text(encoding='utf-8')
                original = content
                
                # Update rootProject.name
                new_content = re.sub(
                    r'rootProject\.name\s*=\s*["\'].*?["\']',
                    f'rootProject.name = "{self.new_app_name}"',
                    content
                )
                
                if original != new_content:
                    settings_file.write_text(new_content, encoding='utf-8')
                    self.logger.info(f"✓ Updated project name in {settings_file}")
                    self.changes['gradle_files'].append(f"{settings_file} (project name updated)")
                else:
                    self.logger.info(f"No changes needed in {settings_file}")

    def rename_package_in_gradle(self):
        """Update package name and namespace in build.gradle"""
        self.logger.info("Starting package name and namespace update in Gradle files...")
        
        # Update settings.gradle files first
        self.update_settings_gradle()
        
        # Check for regular Gradle file
        gradle_file = self.app_dir / 'build.gradle'
        if gradle_file.exists():
            content = gradle_file.read_text(encoding='utf-8')
            original = content
            
            # Update applicationId
            new_content = re.sub(
                r'applicationId\s+[\'"].*?[\'"]',
                f'applicationId "{self.new_package}"',
                content
            )
            
            # Update namespace
            new_content = re.sub(
                r'namespace\s+[\'"].*?[\'"]',
                f'namespace "{self.new_package}"',
                new_content
            )
            
            if original != new_content:
                gradle_file.write_text(new_content, encoding='utf-8')
                self.logger.info(f"✓ Updated applicationId and namespace in {gradle_file}")
                self.changes['gradle_files'].append(f"{gradle_file} (applicationId and namespace updated)")
            else:
                self.logger.info(f"No changes needed in {gradle_file}")
        
        # Check for Kotlin DSL Gradle file
        gradle_kts_file = self.app_dir / 'build.gradle.kts'
        if gradle_kts_file.exists():
            content = gradle_kts_file.read_text(encoding='utf-8')
            original = content
            
            # Update applicationId
            new_content = re.sub(
                r'applicationId\s*=\s*[\'"].*?[\'"]',
                f'applicationId = "{self.new_package}"',
                content
            )
            
            # Update namespace
            new_content = re.sub(
                r'namespace\s*=\s*[\'"].*?[\'"]',
                f'namespace = "{self.new_package}"',
                new_content
            )
            
            if original != new_content:
                gradle_kts_file.write_text(new_content, encoding='utf-8')
                self.logger.info(f"✓ Updated applicationId and namespace in {gradle_kts_file}")
                self.changes['gradle_files'].append(f"{gradle_kts_file} (applicationId and namespace updated)")
            else:
                self.logger.info(f"No changes needed in {gradle_kts_file}")
        
        if not gradle_file.exists() and not gradle_kts_file.exists():
            self.logger.warning(f"Warning: Neither build.gradle nor build.gradle.kts found!")
    
    def update_manifest(self):
        """Update package name in AndroidManifest.xml"""
        self.logger.info("Starting AndroidManifest.xml update...")
        manifest_file = self.main_dir / 'AndroidManifest.xml'
        if manifest_file.exists():
            content = manifest_file.read_text(encoding='utf-8')
            original = content
            new_content = re.sub(
                r'package\s*=\s*[\'"].*?[\'"]',
                f'package="{self.new_package}"',
                content
            )
            
            if original != new_content:
                manifest_file.write_text(new_content, encoding='utf-8')
                self.logger.info(f"✓ Updated package in {manifest_file}")
                self.changes['manifest_files'].append(f"{manifest_file} (package attribute updated)")
            else:
                self.logger.info(f"No changes needed in {manifest_file}")
        else:
            self.logger.warning(f"Warning: {manifest_file} not found!")

        # Also check debug and release manifests if they exist
        for variant in ['debug', 'release']:
            variant_manifest = self.src_dir / variant / 'AndroidManifest.xml'
            if variant_manifest.exists():
                content = variant_manifest.read_text(encoding='utf-8')
                original = content
                new_content = re.sub(
                    r'package\s*=\s*[\'"].*?[\'"]',
                    f'package="{self.new_package}"',
                    content
                )
                
                if original != new_content:
                    variant_manifest.write_text(new_content, encoding='utf-8')
                    self.logger.info(f"✓ Updated package in {variant_manifest}")
                    self.changes['manifest_files'].append(f"{variant_manifest} (package attribute updated)")
                else:
                    self.logger.info(f"No changes needed in {variant_manifest}")

    def update_kotlin_and_java_files(self):
        """Update package statements in Java and Kotlin files"""
        self.logger.info("Starting package statement updates in Java and Kotlin files...")

        old_path = self.java_dir / Path(self.old_package_path)
        new_path = self.java_dir / Path(self.new_package_path)

        if not old_path.exists():
            self.logger.warning(f"Warning: Source directory {old_path} not found!")
            return

        self.logger.info(f"Old source path: {old_path}")
        self.logger.info(f"New source path: {new_path}")

        # Create new directory structure if it doesn't exist
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Recursively process Java and Kotlin files
        def process_dir(directory):
            for item in directory.glob('*'):
                if item.is_dir():
                    process_dir(item)
                elif item.suffix in ['.java', '.kt']:
                    content = item.read_text(encoding='utf-8')
                    original = content

                    # Replace package statements
                    new_content = re.sub(
                        rf'package\s+{self.old_package}(\..*?)?;',
                        lambda m: f'package {self.new_package}{m.group(1) or ""};',
                        content
                    )

                    # Replace imports from the same package
                    new_content = re.sub(
                        rf'import\s+{self.old_package}(\..*?);',
                        lambda m: f'import {self.new_package}{m.group(1)};',
                        new_content
                    )

                    # Calculate new file path correctly
                    rel_path = item.relative_to(old_path)
                    new_file_path = new_path / rel_path

                    # Create parent directories if they don't exist
                    new_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write updated content to new location
                    if original != new_content:
                        new_file_path.write_text(new_content, encoding='utf-8')
                        changes = []
                        if re.search(rf'package\s+{self.old_package}', original):
                            changes.append("package statement")
                        if re.search(rf'import\s+{self.old_package}', original):
                            changes.append("imports")

                        self.logger.info(f"✓ Updated {item} -> {new_file_path} (Updated: {', '.join(changes)})")
                        self.changes['source_files'].append(f"{item} -> {new_file_path} (Updated: {', '.join(changes)})")
                        
                        # Don't delete the original file yet
                        if item != new_file_path:
                            item.touch()  # Update timestamp to mark as processed
                    else:
                        # Copy unchanged file to new location if paths are different
                        if item != new_file_path:
                            shutil.copy2(item, new_file_path)
                            self.logger.info(f"✓ Copied {item} -> {new_file_path} (No content changes needed)")
                            self.changes['source_files'].append(f"{item} -> {new_file_path} (relocated only)")
                            item.touch()  # Update timestamp to mark as processed

        # Process all files in the old package directory
        process_dir(old_path)

        # Only delete the exact old package directory, not shared parts
        if self.old_package != self.new_package:
            try:
                self.logger.info(f"Attempting to remove old package directory: {old_path}")
                shutil.rmtree(old_path)
                self.logger.info(f"✓ Successfully removed old package directory: {old_path}")
            except Exception as e:
                self.logger.error(f"Failed to remove old package directory: {old_path} - {str(e)}")
    
    def generate_summary_report(self):
        """Generate a summary of all changes made"""
        self.logger.info("\n" + "="*50)
        self.logger.info("SUMMARY OF CHANGES")
        self.logger.info("="*50)
        
        self.logger.info(f"\nApp Name Changes ({len(self.changes['app_name'])} files):")
        for change in self.changes['app_name']:
            self.logger.info(f"  - {change}")
            
        self.logger.info(f"\nGradle Files ({len(self.changes['gradle_files'])} files):")
        for change in self.changes['gradle_files']:
            self.logger.info(f"  - {change}")
            
        self.logger.info(f"\nManifest Files ({len(self.changes['manifest_files'])} files):")
        for change in self.changes['manifest_files']:
            self.logger.info(f"  - {change}")
            
        self.logger.info(f"\nSource Files ({len(self.changes['source_files'])} files):")
        for change in self.changes['source_files']:
            self.logger.info(f"  - {change}")
            
        total_files = (len(self.changes['app_name']) + len(self.changes['gradle_files']) + 
                       len(self.changes['manifest_files']) + len(self.changes['source_files']))
        
        self.logger.info("\n" + "="*50)
        self.logger.info(f"TOTAL FILES MODIFIED: {total_files}")
        self.logger.info("="*50)
    
    def run(self):
        """Run all renaming operations"""
        self.logger.info(f"Starting Android project renaming from '{self.old_app_name}' to '{self.new_app_name}'")
        self.logger.info(f"Package rename: {self.old_package} -> {self.new_package}")
        
        self.rename_app_name()
        self.rename_package_in_gradle()
        self.update_manifest()
        self.update_kotlin_and_java_files()
        self.generate_summary_report()
        
        self.logger.info("\nRenaming completed. You may need to rebuild your project in Android Studio.")
        self.logger.info("Note: You might still need to manually update some references like custom deep links.")

def main():
    parser = argparse.ArgumentParser(description='Rename Android project components')
    parser.add_argument('--project', required=True, help='Path to the Android project root directory')
    parser.add_argument('--old-app-name', required=True, help='Old app name as in strings.xml')
    parser.add_argument('--new-app-name', required=True, help='New app name to set in strings.xml')
    parser.add_argument('--old-package', required=True, help='Old package name (e.g., com.example.oldapp)')
    parser.add_argument('--new-package', required=True, help='New package name (e.g., com.example.newapp)')
    parser.add_argument('--log-file', help='Path to output log file (default: auto-generated)')
    
    args = parser.parse_args()
    
    renamer = AndroidProjectRenamer(
        project_path=args.project,
        old_app_name=args.old_app_name,
        new_app_name=args.new_app_name,
        old_package=args.old_package,
        new_package=args.new_package,
        log_file=args.log_file
    )
    
    renamer.run()

if __name__ == '__main__':
    main()
