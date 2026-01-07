"""
Test script to verify Groq LLM integration
"""

import os
import sys

# Load .env file manually
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print(f"✓ Loaded .env file from {env_path}\n")

# Import enhancer
from src.llm_enhancer import get_enhancer

# Test LLM enhancement
enhancer = get_enhancer()

print("=" * 60)
print("Groq LLM Enhancement Test")
print("=" * 60)
print(f"API Key Set: {bool(enhancer.api_key)}")
print(f"Model: {enhancer.model}")
print(f"LLM Enabled: {enhancer.enabled}")
print()

if enhancer.enabled:
    print("Testing Task Description Enhancement...")
    print("(Note: If you get 403 error, check Groq API key validity)")
    desc = enhancer.generate_task_description("Add user authentication", "engineering")
    if desc:
        print(f"✓ Task Description:\n  {desc}\n")
    else:
        print("✗ LLM unavailable - using default templates\n")
    
    print("Testing Comment Enhancement...")
    comment = enhancer.generate_comment("Optimize database queries", "Engineer")
    if comment:
        print(f"✓ Comment:\n  {comment}\n")
    else:
        print("✗ LLM unavailable - using default templates\n")
    
    print("=" * 60)
    print("LLM Integration Status: Ready (fallback to templates if needed)")
    print("=" * 60)
else:
    print("⚠ LLM not configured - using default content generation")
    print("To enable, set GROQ_API_KEY in .env file")
    print()
    print("Note: Even without LLM, generator produces high-quality data")
    print("      using realistic templates and distributions.")
