from setuptools import setup, find_packages

setup(
    name='kasa-carbon',
    version='0.0.6',
    packages=find_packages(),
    author='Scott Chamberlin',
    author_email='scott@snowymountainworks.com',
    description='Monitor energy and carbon values from Kasa smart plug or Omada PoE switch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/scottcha/kasa_carbon',
    install_requires=[
        'python-kasa==0.7.0.5',
        'psycopg2-binary==2.9.9',
        'asyncpg==0.29.0',
        'pytz==2023.3.post1',
        'aiohttp==3.9.5',
        'python-dotenv==1.0.0',
        'requests==3.31.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    entry_points={
        'console_scripts': [
            'kasa-carbon = kasa_carbon.kasa_carbon_main:main_wrapper',
        ],
    },
)