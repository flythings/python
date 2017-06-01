from distutils.core import setup
setup(
  name = 'flythings',
  packages = ['flythings'], # this must be the same as the name above
  version = '0.6',
  description = 'A python library to add observations into flythings',
  author = 'flythings',
  author_email = 'gblazquez@itg.es',
  license='MIT',
  url = 'https://github.com/flythings/python', # use the URL to the github repo
  download_url = 'https://github.com/flythings/python/0.6.tar.gz', # I'll explain this in a second
  keywords = ['flythings'], # arbitrary keywords
  classifiers = [],
  install_requires=[
   'requests'
  ]
)