from setuptools import setup


# from pathlib import Path

# CURRENT_DIR = Path(__file__).parent


def get_long_description():
    readme_md = "README.md"
    with open(readme_md) as ld_file:
        return ld_file.read()


setup(
    name='flythings',
    packages=['flythings'],
    version='2.0.0',
    description='A python library to add ans search observations into flythings',
    author='flythings',
    author_email='fly@itg.es',
    license='GPL-3.0',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",  # This is important!
    url='https://github.com/flythings/python',
    download_url='https://github.com/flythings/python/2.0.0.tar.gz',
    keywords=['flythings', 'IoT'],
    install_requires=['requests', 'enum34'],
    classifiers=[]
)
