from setuptools import setup, find_packages

setup(
    name='qsra_qcra',
    version='2.2.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'click',
        'openpyxl>=3.1.0',
        'dash',
        'plotly'
    ],
    entry_points={
        'console_scripts': [
            'qsra_qcra=qsra_qcra.cli:cli',
        ],
    },
)
