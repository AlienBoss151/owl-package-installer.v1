from setuptools import setup, find_packages

setup(
    name="opi",
    version="1.1.0",
    description="Owl wizard package builder for Python projects",
    author="Lordcarlos Onwuka",
    author_email="lordcarlos151@gmail.com",  # Email me for colabo 
    url="https://github.com/AlienBoss151/owl-package-installer.v1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "opi=opi.cli:main",
        ],
    },
    python_requires=">=3.10",
    include_package_data=True,
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
)