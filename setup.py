from setuptools import setup

setup(
    name="eidex",
    version="0.1.0",
    py_modules=["eidex"],
    install_requires=["gitpython>=3.1.0"],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "flake8>=7.0.0",
            "black>=25.0.0",
            "isort>=6.0.0",
        ],
    },
    description="Branch-aware AI logging for development workflows",
    author="Your Name",
    author_email="your.email@example.com",
    entry_points={"console_scripts": ["eidex = eidex:main"]},
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
