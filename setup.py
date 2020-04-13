import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sgp30',
    version='1.0.0',
    description='Python module for reading SPG30 gas sensor values on raspberry pi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/oliverbinns/sgp30',
    author='Oliver Binns',
    author_email='contact@oliverbinns.com',
    license='MIT',
    packages=setuptools.find_packages(exclude=['contrib']),
    install_requires=['pandas>=0.20'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
