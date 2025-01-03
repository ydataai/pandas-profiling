from pathlib import Path

from setuptools import setup

# Read the contents of README file
source_root = Path(".")
with (source_root / "README.md").open(encoding="utf-8") as f:
    long_description = f.read()

try:
    version = (source_root / "VERSION").read_text().rstrip("\n")
except FileNotFoundError:
    version = "0.0.dev0"

with open(source_root / "src/ydata_profiling/version.py", "w") as version_file:
    version_file.write(f"__version__ = '{version}'")

setup(
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    options={"bdist_wheel": {"universal": True}},
)
