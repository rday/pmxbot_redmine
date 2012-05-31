from setuptools import find_packages

setup_params = dict(
    name="pmxbot-redmine",
    version="0.1",
    packages=find_packages(),
    entry_points=dict(
        pmxbot_handlers = [
            'pmxbot_redmine=pmxbot_redmine.redmine:Redmine.entry',
        ]
    ), 
    install_requires=[
        "pmxbot>=1005",
        "requests",
    ],
    description="Integrate Redmine with the PMXBOT",
    license = 'MIT',
    author="Ryan Day",
    author_email="ryanday2@gmail.com",
    maintainer = 'rday',
    maintainer_email = 'ryanday2@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
)

if __name__ == '__main__':
    from setuptools import setup
    setup(**setup_params)
