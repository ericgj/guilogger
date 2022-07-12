from setuptools import setup, find_packages

tests_require = []

setup(
    name="guilogger",
    version="0.4",
    description="GUI logger + progress bar",
    license="MIT",
    author="Eric Gjertsen",
    email="ericgj72@gmail.com",
    url="https://github.com/ericgj/guilogger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    install_requires=[],
    tests_require=tests_require,
    extras_require={"test": tests_require},  # to make pip happy
    zip_safe=False,  # to make mypy happy
)
