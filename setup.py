import setuptools

setuptools.setup(
    name='django-asyncio-tasks',
    version='2021.4.7',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=setuptools.find_packages()
)
