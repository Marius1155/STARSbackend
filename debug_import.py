import sys
import os
import traceback

print("=== DIAGNOSTIC INFO ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Directory contents: {os.listdir('.')}")

print("\n=== TRYING TO IMPORT STARS ===")
try:
    import STARS

    print("✓ Successfully imported 'STARS'")
    print(f"STARS module file: {STARS.__file__}")
    print(f"STARS module contents: {dir(STARS)}")
except Exception as e:
    print(f"✗ Failed to import 'STARS': {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== TRYING TO IMPORT STARS.APPS ===")
try:
    from STARS.apps import StarsConfig

    print("✓ Successfully imported StarsConfig")
    print(f"StarsConfig: {StarsConfig}")
except Exception as e:
    print(f"✗ Failed to import StarsConfig: {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== CHECKING STARS DIRECTORY ===")
if os.path.exists('STARS'):
    print("✓ STARS directory exists")
    print(f"STARS directory contents: {os.listdir('STARS')}")

    if os.path.exists('STARS/__init__.py'):
        print("✓ STARS/__init__.py exists")
    else:
        print("✗ STARS/__init__.py missing")

    if os.path.exists('STARS/apps.py'):
        print("✓ STARS/apps.py exists")
        with open('STARS/apps.py', 'r') as f:
            print(f"STARS/apps.py content:\n{f.read()}")
    else:
        print("✗ STARS/apps.py missing")
else:
    print("✗ STARS directory doesn't exist")