import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()



setuptools.setup(
    name="pikax",
    version="2.0.12",
    author="Redcxx",
    author_email="weilue.luo@student.manchester.ac.uk",
    description="A Pixiv Mass Downloading Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Redcxx/Pikax",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Topic :: Utilities"
    ],
)
