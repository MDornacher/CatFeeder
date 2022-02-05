from setuptools import setup

setup(
    name="CatFeeder",
    version="0.0.1",
    package_dir={"": "catfeeder"},
    url="https://github.com/MDornacher/CatFeeder",
    license="MIT License",
    author="Manuel Dornacher",
    author_email="manuel.dornacher@gmail.com",
    description="Distinguish cats with automated cat feeder",
    install_requires=[
        "RPi.GPIO",
        "loguru",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
        ]
    },
)
