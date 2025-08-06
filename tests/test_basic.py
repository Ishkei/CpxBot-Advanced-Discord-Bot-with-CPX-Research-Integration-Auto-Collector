"""
Basic Tests for Survey Bot

Simple tests to verify the project setup and basic functionality.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import pytest
from utils.config_manager import ConfigManager


def test_config_manager():
    """Test the configuration manager."""
    try:
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # Check that config is loaded
        assert config is not None
        assert "discord" in config
        assert "cpx_research" in config
        
        print("✅ Configuration manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")
        return False


def test_project_structure():
    """Test that the project structure is correct."""
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "config.yaml",
        "src/__init__.py",
        "src/discord_bot/__init__.py",
        "src/utils/__init__.py",
        "src/web_scraper/__init__.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            return False
    
    print("✅ Project structure test passed")
    return True


def test_imports():
    """Test that all modules can be imported."""
    try:
        from discord_bot.bot import SurveyBot
        from utils.config_manager import ConfigManager
        from utils.database_manager import DatabaseManager
        from src.web_scraper.cpx_scraper import CPXScraper
        
        print("✅ Import test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False


if __name__ == "__main__":
    print("Running basic tests...")
    
    tests = [
        test_project_structure,
        test_imports,
        test_config_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Project setup is correct.")
    else:
        print("⚠️  Some tests failed. Please check the setup.") 