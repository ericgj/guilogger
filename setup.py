from setuptools import setup, find_packages

tests_require = ["pytest", "pytest-random-order"]

setup(
    name="guilogger",
    version="0.1",
    description="GUI Logger",
    license="MIT",
    author="Eric Gjertsen",
    email="eric.gjertsen@clario.com",
    packages=find_packages(),
    install_requires=[],
    tests_require=tests_require,
    extras_require={"test": tests_require},  # to make pip happy
    zip_safe=False,  # to make mypy happy
)

