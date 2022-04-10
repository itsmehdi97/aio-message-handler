import os
from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader


module = SourceFileLoader(
    "version", os.path.join("aio_message_handler", "version.py")
).load_module()


setup(
    name="aio-message-handler",
    version=module.__version__,
    author=module.__author__,
    author_email=module.team_email,
    license=module.package_license,
    description=module.package_info,
    long_description=open("README.md").read(),
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(exclude=["tests"]),
    package_data={"aio_message_handler": ["py.typed"]},
    install_requires=["aio-pika>=6.8.0,<9", ],
    python_requires=">=3.5, <4",
    extras_require={
        "develop": [
            "aio-pika",
            "async_generator",
            "coverage!=4.3",
            "coveralls",
            "pylava",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "shortuuid",
            "nox",
            "sphinx",
            "sphinx-autobuild",
            "timeout-decorator",
            "tox>=2.4",
        ],
    },
    project_urls={
        "Documentation": "https://aio-message-handler.readthedocs.org/",
        "Source": "https://github.com/itsmehdi97/aio-message-handler",
    },
)
