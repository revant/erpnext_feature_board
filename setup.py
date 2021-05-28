from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in erpnext_feature_board/__init__.py
from erpnext_feature_board import __version__ as version

setup(
	name='erpnext_feature_board',
	version=version,
	description='Feature board for ERPNext',
	author='ERPNext Community',
	author_email='community@erpnext.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
