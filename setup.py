from setuptools import setup

import camgi


dependencies = ['jinja2']


setup(
    name='camgi',
    version=camgi.version,
    license='GPLv3',
    author='michael mccune',
    author_email='msm@opbstudios.com',
    packages=['camgi'],
    install_requires=dependencies,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'camgi = camgi.main:main',
        ],
    }
)
