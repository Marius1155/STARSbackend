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
    import Stars

    print("✓ Successfully imported 'Stars'")
    print(f"Stars module file: {Stars.__file__}")
    print(f"Stars module contents: {dir(Stars)}")
except Exception as e:
    print(f"✗ Failed to import 'Stars': {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== TRYING TO IMPORT STARS.APPS ===")
try:
    from Stars.apps import StarsConfig

    print("✓ Successfully imported StarsConfig")
    print(f"StarsConfig: {StarsConfig}")
except Exception as e:
    print(f"✗ Failed to import StarsConfig: {e}")
    print(f"Full traceback: {traceback.format_exc()}")

print("\n=== CHECKING STARS DIRECTORY ===")
if os.path.exists('Stars'):
    print("✓ Stars directory exists")
    print(f"Stars directory contents: {os.listdir('Stars')}")

    if os.path.exists('Stars/__init__.py'):
        print("✓ Stars/__init__.py exists")
    else:
        print("✗ Stars/__init__.py missing")

    if os.path.exists('Stars/apps.py'):
        print("✓ Stars/apps.py exists")
        with open('Stars/apps.py', 'r') as f:
            print(f"Stars/apps.py content:\n{f.read()}")
    else:
        print("✗ Stars/apps.py missing")
else:
    print("✗ Stars directory doesn't exist")