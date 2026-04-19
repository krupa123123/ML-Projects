import sys

def test_imports():
    """Verify all dependencies work"""
    tests = {
        "openai": False,
        "whisper": False,
        "streamlit": False,
        "numpy": False,
        "pandas": False,
        "matplotlib": False,
        "sqlite3": False,
        "sounddevice": False,
    }
    
    for module in tests:
        try:
            __import__(module)
            tests[module] = True
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
    
    print(f"\nPassed: {sum(tests.values())}/{len(tests)}")
    return all(tests.values())

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)