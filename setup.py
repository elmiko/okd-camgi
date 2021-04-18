from setuptools import setup

import okd_camgi


with open('README.md', 'r', encoding='utf-8') as readmefile:
    readme = readmefile.read()


dependencies = [
    'jinja2',
    'bottle',
    'pyyaml',
    'pygments',
]


setup(
    name='okd-camgi',
    version=okd_camgi.version,
    license='GPLv3',
    author='michael mccune',
    author_email='msm@opbstudios.com',
    description='OKD Cluster Autoscaler Must Gather Investigator',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/elmiko/okd-camgi",
    packages=['okd_camgi'],
    install_requires=dependencies,
    package_data={
        'okd_camgi': ["templates/*.html"],
    },
    entry_points={
        'console_scripts': [
            'okd-camgi = okd_camgi.main:main',
        ],
    }
)
