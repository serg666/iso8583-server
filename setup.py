import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

with open(os.path.join(here, 'requirements.txt')) as f:
    req_lines = [line.strip() for line in f.readlines()]

    def fix_url_line(line):
        if '#egg=' in line:
            return line.rsplit('#egg=', 1)[1]
        return line
    requires = [fix_url_line(line) for line in req_lines if line]

version = '0.1'

setup(name='ISO8583Server',
      version=version,
      description='ISO8583 Server',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
      ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      serve = server:serve
      """,
      )
