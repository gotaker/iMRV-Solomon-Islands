from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mrvtools/__init__.py
from mrvtools import __version__ as version

setup(
	name="mrvtools",
	version=version,
	description="mrvtools",
	author="tridotstech",
	author_email="info@tridotstech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
