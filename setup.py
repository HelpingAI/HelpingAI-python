from setuptools import setup, find_packages

from HelpingAI.version import VERSION


# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="HelpingAI",
    version=VERSION,  # noqa: F821
    description="Python client library for the HelpingAI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HelpingAI",
    author_email="helpingaiemotional@gmail.com",
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
