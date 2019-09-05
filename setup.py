from setuptools import setup, find_packages

setup(
    name='JJ_measurements',
    version='0.1',
    description="Experiment code for JJ measurements",
    url='https://github.com/QNLSydney/JJ_measurements',
    packages=find_packages(),
    install_requires=[
        'qcodes>=0.4',
        'numpy',
        'matplotlib'
    ],
    python_requires='>3.6'
)
