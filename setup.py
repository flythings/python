from distutils.core import setup
setup(
  name = 'flythings',
  packages = ['flythings'],
  version = '0.9.3',
  description = 'A python library to add ans search observations into flythings',
  author = 'flythings',
  author_email = 'tic@itg.es',
  license='GPL-3.0',
  url = 'https://github.com/flythings/python',
  download_url = 'https://github.com/flythings/python/0.9.3.tar.gz',
  keywords = ['flythings', 'IoT'],
  classifiers = [],
  install_requires=[
   'requests'
  ]
)