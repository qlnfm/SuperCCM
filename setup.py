from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read().splitlines()


setup(
    name='superccm',
    version='1.1.1',
    author='Qincheng Qiao',
    author_email='jugking6688@gmail.com',
    description='Open-Source Framework for Corneal Nerve Image Analysis',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/qlnfm/SuperCCM',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    package_data={
        "superccm": ["impl/segment/ccm.onnx", 'impl/utils/ref.png'],
    },
    python_requires='>=3.10',
    install_requires=parse_requirements('requirements.txt'),
    include_package_data=True
)

# pip install --upgrade build twine
# python setup.py sdist bdist_wheel
# twine upload dist/*
