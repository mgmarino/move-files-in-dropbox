from setuptools import find_packages, setup

setup(
    name="move_files",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "dropbox",
        "s3fs",
    ],
    python_requires=">=3.6",
)
