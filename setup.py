try:
	import pypandoc
	readme = pypandoc.convert_file("README.md", "rst")
except:
	readme = open("README.md").read()

from setuptools import setup, find_packages
setup(
	name = "clirender",
	version = "0.14",
	description = "CLI rendering engine for Python",
	long_description = readme,
	install_requires = ["colorama", "numexpr", "lxml"],
	packages = find_packages(),
	author = "Ivanq",
	author_email = "imachug@gmail.com",
	url = "https://github.com/imachug/clirender",
	keywords = ["cli", "cli-application", "rendering-2d-graphics"],
	classifiers = []
)