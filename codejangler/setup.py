from setuptools import setup, find_packages

setup(
    name="codejangler",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "crewai-tools>=0.17.0",
        "gitpython>=3.1.0",
        "pygithub>=2.1.0",
        "pydantic>=2.6.1",
    ],
    entry_points={
        "console_scripts": [
            "codejangler=codejangler.cli:cli",
        ],
    },
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for optimizing GitHub pull requests using AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/codejangler",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
