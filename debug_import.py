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
    import stars

    print("✓ Successfully imported 'stars'")
    print(f"Stars module file: {stars.__file__}")
    print(f"Stars module contents: {dir(stars)}")
except Exception as e:
    print(f"✗ Failed to import 'stars': {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== TRYING TO IMPORT STARS.APPS ===")
try:
    from stars.apps import StarsConfig

    print("✓ Successfully imported StarsConfig")
    print(f"StarsConfig: {StarsConfig}")
except Exception as e:
    print(f"✗ Failed to import StarsConfig: {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== CHECKING STARS DIRECTORY ===")
if os.path.exists('stars'):
    print("✓ Stars directory exists")
    print(f"Stars directory contents: {os.listdir('stars')}")

    if os.path.exists('stars/__init__.py'):
        print("✓ stars/__init__.py exists")
    else:
        print("✗ stars/__init__.py missing")

    if os.path.exists('stars/apps.py'):
        print("✓ stars/apps.py exists")
        with open('stars/apps.py', 'r') as f:
            print(f"stars/apps.py content:\n{f.read()}")
    else:
        print("✗ stars/apps.py missing")
else:
    print("✗ Stars directory doesn't exist")