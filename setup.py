from setuptools import setup, find_packages


with open('requirements.txt') as f:
    # Get eligible lines
    raw_lines = [
        line for line in f.readlines()
        if not line.startswith('#') and
        not line.startswith('--') and
        line != '\n'
    ]
    requirements = [
        line.split(' ')[0].strip('\n') for line in raw_lines
    ]


setup(
    name='referral_app',
    description='App for catching signups and referrals',
    version='0.1.0',
    author='Alejandro Moro Fernandez',
    author_email='',
    packages=find_packages(),
    install_requires=requirements,
)