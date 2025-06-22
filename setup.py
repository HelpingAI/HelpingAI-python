from setuptools import setup, find_packages
import os


def get_version():
    """Get version from version.py without importing the package."""
    version_file = os.path.join(os.path.dirname(__file__), "HelpingAI", "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("VERSION"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")


# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="HelpingAI",
    version=get_version(),
    description="Python client library for the HelpingAI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HelpingAI",
    author_email="varun@helpingai.co",
    url="https://github.com/HelpingAI/HelpingAI-python",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "requests",
        "typing_extensions"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Documentation": "https://helpingai.co/docs",
        "Source": "https://github.com/HelpingAI/HelpingAI-python",
        "Tracker": "https://github.com/HelpingAI/HelpingAI-python/issues",
    },
)
