from setuptools import setup, find_packages

setup(
    name='hannibal',
    version='0.0.9',
    author='JorgenLiu',
    author_email='avalon852456@gmail.com',
    url='https://github.com/JorgenLiu/hannibal',
    maintainer='JorgenLiu',
    maintainer_email='avalon852456@gmail.com',
    license='MIT License',
    description=u'A light-weight crawler framework based on asyncio, aiohttp and redis.',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'asyncio',
        'redis',
        'requests',
        'async-timeout'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
