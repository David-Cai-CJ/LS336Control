from setuptools import setup, find_packages
from ls336 import __version__

setup(name='LS336Control',
      version=__version__,
      description='Lakeshore 336 Temperature control interface',
      long_description=open('README.md').read(),
      author='Siwick Lab',
      author_email='sebastian.hammer@mail.mcgill.ca',
      url='https://github.com/HammerSeb/LS336Control',
      packages= find_packages(),
      install_requires=['numpy', 'PyQT5', 'pyqtgraph','lakeshore','pyqtdarktheme'],
      include_package_data = True
     )