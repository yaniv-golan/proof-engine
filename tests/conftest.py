import sys
import os

# Add github-pages root to path for tools.lib imports
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# Add proof-engine scripts to path so tests can import them
SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "proof-engine", "skills", "proof-engine"
)
sys.path.insert(0, SCRIPTS_DIR)


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: slow test (full-site build)")
