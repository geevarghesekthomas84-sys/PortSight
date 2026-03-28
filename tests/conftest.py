import os
import sys

# Add the root directory to sys.path so that 'portsight' is importable during tests
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
