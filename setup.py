from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read().splitlines()


setup(
    name='superccm',
    version='0.1.0',
    author='Qincheng Qiao',
    author_email='jugking6688@gmail.com',
    description='An Open-Source Python Toolkit for Automated Quantification of Corneal Nerve Fibers in Confocal Microscopy Images',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://https://github.com/SummerColdWind',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    python_requires='>=3.9',
    install_requires=parse_requirements('requirements.txt'),
    include_package_data=True
)
