from setuptools import setup

import okd_camgi


dependencies = ['jinja2']


setup(
    name='okd-camgi',
    version=camgi.version,
    license='GPLv3',
    author='michael mccune',
    author_email='msm@opbstudios.com',
    packages=['okd_camgi'],
    install_requires=dependencies,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'okd-camgi = okd_camgi.main:main',
        ],
    }
)
