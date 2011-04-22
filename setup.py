from setuptools import setup, find_packages


setup(
    name="re-eat",
    version="0.1",
    packages=find_packages(),

    author="Georges Dubus",
    author_email="georges.dubus@compiletoi.net",
#    description = "This is an Example Package",
    license="GPLv3",
#    keywords = "hello world example examples",
#    url = "http://example.com/HelloWorld/",   # project home page, if any

    install_requires=['SQLAlchemy'],

     entry_points={
#        'console_scripts': [
#            'foo = my_package.some_module:main_func',
#            'bar = other_module:some_func',
#        ],
        'gui_scripts': [
            're-eat = re_eat.main:main',
        ]
    }
)
