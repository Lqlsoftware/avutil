import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="avutil",
    version="1.1.1",
    author="Everyone",
    description="Provide some useful utils for tidying up your AV folder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4.0',
    install_requires=[
      'beautifulsoup4 >= 4.7.0',
      'requests >= 2.21.0',
    ],
    entry_points={
        'console_scripts': [
            'tidyup = tidy_up:main'
        ]
    },
    scripts=['avutil/tidy_up.py'],
)
