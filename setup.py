import setuptools

TESTS_REQUIRE = [
    "black",
    "coverage",
    "codecov",
    "codespell",
    "flake8",
    "flake8-blind-except",
    "flake8-builtins",
    "flake8-commas",
    "flake8-debugger",
    "flake8-docstrings",
    "flake8-isort",
    "flaky",
    "isort",
    "pytest",
    "pytest-xdist",
    "pytype",
]

setuptools.setup(
    name="dmc2gym",
    version="1.1.0",
    author="Yawen Duan and Denis Yarats",
    description=("a gym like wrapper for dm_control"),
    license="",
    python_requires=">=3.9.0",
    keywords="gym dm_control openai deepmind",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "setuptools",
        "gym",
        "dm_control",
    ],
    classifiers=["Programming Language :: Python :: 3"],
    tests_require=TESTS_REQUIRE,
    extras_require={"test": TESTS_REQUIRE},
)
