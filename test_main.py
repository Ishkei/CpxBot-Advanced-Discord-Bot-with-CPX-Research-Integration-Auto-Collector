#!/usr/bin/env python3
"""
Test script for main.py components
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all main.py imports work correctly."""
    try:
        from dotenv import load_dotenv
        print("✅ dotenv imported successfully")
        
        from loguru import logger
        print("✅ loguru imported successfully")
        
        import yaml
        print("✅ yaml imported successfully")
        
        from src.discord_bot.bot import SurveyBot
        print("✅ SurveyBot imported successfully")
        
        from src.utils.config_manager import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from src.utils.database_manager import DatabaseManager
        print("✅ DatabaseManager imported successfully")
        
        print("\n🎉 All imports successful! main.py should work correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from src.utils.config_manager import ConfigManager
        
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        print("✅ Configuration loaded successfully")
        print(f"   Database URL: {config.get('database', {}).get('url', 'Not found')}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing main.py components...")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Test configuration
    config_ok = test_config()
    print()
    
    if imports_ok and config_ok:
        print("✅ All tests passed! main.py is ready to run.")
        print("\nTo run the Discord bot:")
        print("1. Set up your DISCORD_TOKEN in .env file")
        print("2. Configure your database")
        print("3. Run: python3 main.py")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 