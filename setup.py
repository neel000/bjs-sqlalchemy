from setuptools import setup, find_packages

setup(
    name='bjs-sqlalchemy',
    version='0.1',
    packages=find_packages(),
    install_requires=["sqlalchemy", "pydantic", "aiosqlite"],
    description='Sqlalchemy Filter package will help you to filtering your data on sqlalchemy query.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Indranil Swarnakar',
    author_email='indranil.swarnakar@gmail.com',
    url='https://github.com/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
