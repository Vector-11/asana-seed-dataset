"""
Version Information for Asana Seed Data Generator
Shows all libraries and their versions used in this project
"""

import sys
import sqlite3
import json
import os
import logging
import uuid
import random
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
from urllib import request, error


def get_library_versions():
    """Get all libraries and their versions used in this project"""
    
    versions = {
        "Project": {
            "name": "Asana Seed Data Generator",
            "version": "1.0.0",
            "status": "Production Ready",
            "llm_enhancement": "Groq LLM Integration (optional)",
            "created": "January 5, 2026"
        },
        "Python": {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "implementation": sys.implementation.name,
            "platform": sys.platform
        },
        "Built-in Libraries": {
            "sqlite3": sqlite3.version,
            "sys": "built-in",
            "os": "built-in",
            "json": "built-in",
            "logging": "built-in",
            "random": "built-in",
            "uuid": "built-in",
            "datetime": "built-in",
            "dataclasses": "built-in",
            "enum": "built-in",
            "typing": "built-in",
            "urllib": "built-in",
            "urllib.request": "built-in",
            "urllib.error": "built-in"
        },
        "External Libraries": {
            "status": "NONE - Zero external dependencies",
            "count": 0,
            "reason": "Pure Python with stdlib only"
        },
        "Optional Libraries (if installed)": {
            "dotenv": "for .env file loading (optional, not required)",
            "groq": "for Groq API client (if using LLM enhancement)"
        }
    }
    
    return versions


def print_version_info():
    """Print version information in a formatted way"""
    
    versions = get_library_versions()
    
    print("\n" + "="*70)
    print("ASANA SEED DATA GENERATOR - VERSION & LIBRARY INFORMATION")
    print("="*70 + "\n")
    
    # Project Info
    print("📦 PROJECT INFORMATION")
    print("-" * 70)
    for key, value in versions["Project"].items():
        print(f"  {key:.<30} {value}")
    
    # Python Info
    print("\n🐍 PYTHON ENVIRONMENT")
    print("-" * 70)
    for key, value in versions["Python"].items():
        print(f"  {key:.<30} {value}")
    
    # Built-in Libraries
    print("\n✅ BUILT-IN LIBRARIES (No installation required)")
    print("-" * 70)
    for lib, ver in versions["Built-in Libraries"].items():
        print(f"  {lib:.<30} {ver}")
    
    # External Dependencies
    print("\n⭐ EXTERNAL DEPENDENCIES")
    print("-" * 70)
    for key, value in versions["External Libraries"].items():
        if key != "count":
            print(f"  {key:.<30} {value}")
    
    # Optional Libraries
    print("\n🔧 OPTIONAL LIBRARIES (Enhanced features)")
    print("-" * 70)
    for lib, desc in versions["Optional Libraries (if installed)"].items():
        print(f"  {lib:.<30} {desc}")
    
    print("\n" + "="*70)
    print("✅ SUMMARY: ZERO EXTERNAL DEPENDENCIES REQUIRED")
    print("="*70 + "\n")


def get_version_dict():
    """Return versions as a dictionary for programmatic access"""
    return get_library_versions()


def check_library_installed(library_name):
    """Check if a library is installed and get its version"""
    try:
        if library_name == "sqlite3":
            return sqlite3.version
        else:
            module = __import__(library_name)
            if hasattr(module, '__version__'):
                return module.__version__
            else:
                return "built-in or version not available"
    except ImportError:
        return "not installed"


if __name__ == "__main__":
    print_version_info()
    
    print("\n📋 DETAILED LIBRARY BREAKDOWN:")
    print("="*70)
    
    print("\n🔹 Core Python Modules Used:")
    core_modules = [
        "sqlite3", "sys", "os", "json", "logging", "random", "uuid",
        "datetime", "dataclasses", "enum", "typing", "urllib"
    ]
    for module in core_modules:
        version = check_library_installed(module)
        print(f"  • {module:.<30} {version}")
    
    print("\n🔹 Optional/External Libraries:")
    optional_libs = ["dotenv", "groq"]
    for lib in optional_libs:
        version = check_library_installed(lib)
        status = "✅ INSTALLED" if version != "not installed" else "❌ NOT INSTALLED (optional)"
        print(f"  • {lib:.<30} {version} [{status}]")
    
    print("\n" + "="*70)
    print("✨ Project uses ZERO required external dependencies!")
    print("✨ All functionality works with Python 3.8+ standard library")
    print("="*70 + "\n")
