import re
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('./twikit/__init__.py') as f:
    version = re.findall(r"__version__ = '(.+)'", f.read())[0]

setup(
    name='twikit-xero',
    version=version,
    packages=find_packages(),
    install_requires=[
        'httpx[socks]',
        'curl_cffi>=0.7',
        'filetype',
        'beautifulsoup4',
        'pyotp',
        'lxml',
        'webvtt-py',
        'm3u8',
    ],
    python_requires='>=3.10',
    description='X API wrapper with browser-grade TLS. Fork of d60/twikit.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/xer0xde/twikit-xero',
    package_data={'twikit': ['py.typed']},
)
