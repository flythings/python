from distutils.core import setup
setup(
  name = 'flythings',
  packages = ['flythings'],
  version = '0.9.0',
  description = 'A python library to add observations into flythings',
  author = 'flythings',
  author_email = 'gblazquez@itg.es',
  license='GPL-3.0',
  url = 'https://github.com/flythings/python',
  download_url = 'https://github.com/flythings/python/0.9.0.tar.gz',
  keywords = ['flythings'],
  classifiers = [],
  install_requires=[
   'requests'
  ]
)