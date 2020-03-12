from setuptools import setup

setup(
    name="discount-checker",
    version="1.0.0",
    url="https://github.com/desmondch/discount-checker",
    author="Desmond Cheang",
    author_email="desmondcheang99@gmail.com",
    description="CLI tool to check supermarkets webpages for sales on items of interest",
    packages=["discount_checker", "discount_checker.item"],
    include_package_data=True,
    entry_points={
        "console_scripts": ["discount-check=discount_checker.cli:main"]
    },
    install_requires=[
        "aiohttp",
        "pydantic",
        "pyyaml"
    ],
)
