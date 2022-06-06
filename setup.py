__author__ = 'Yevhenii Dits'

import setuptools


setuptools.setup(
    name='sgs',
    version='0.0.1',
    license='MIT',
    author='Yevhenii Dits',
    author_email='yevheniidits@gmail.com',
    description='Simple Google Services. Simplifies interaction with Google API in the most frequently used tasks.',
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=(
        'google-api-python-client==2.49.0',
        'google-auth-oauthlib==0.5.1'
    )
)
