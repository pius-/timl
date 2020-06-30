import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timl",
    version="0.0.1",
    author="Pius Surendralal",
    author_email="pius.surendralal@gmail.com",
    description="JIRA Time Logger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pius-/timl",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyyaml>=5.3.1',
        'requests>=2.18.4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["timl = timl.__main__:main"]},
)
