from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_side_menu/__init__.py
from frappe_side_menu import __version__ as version

setup(
	name="frappe_side_menu",
	version=version,
	description="Frappe Side Menu",
	author="NetZeroLabs",
	author_email="info@netzerolabs.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
