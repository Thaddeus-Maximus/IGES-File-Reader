import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="IGES-File-Reader-Thaddeus-Maximus",
	version="0.0.2",
	author="Thaddeus Hughes",
	author_email="hughes.thad@gmail.com",
	description="Utility for reading data from IGES files",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Thaddeus-Maximus/IGES-File-Reader",
	packages=['iges'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)