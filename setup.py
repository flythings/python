from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='flythings',
    packages=['flythings'],
    version='1.2.0',
    description='A python library to add ans search observations into flythings',
    author='flythings',
    author_email = 'tic@itg.es',
    license='GPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    url='https://github.com/flythings/python',
    download_url='https://github.com/flythings/python/1.2.0.tar.gz',
    keywords=['flythings', 'IoT'],
    install_requires=['requests'],
    classifiers=[]
)
