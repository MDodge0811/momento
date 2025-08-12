from setuptools import setup

setup(
    name="momento",
    version="0.1.0",
    py_modules=["momento"],
    install_requires=["gitpython>=3.1.0"],
    description="Branch-aware AI logging for development workflows",
    author="Your Name",
    author_email="your.email@example.com",
    entry_points={
        "console_scripts": [
            "momento = momento:main"
        ]
    }
)