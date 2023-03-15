from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='mkdocs-changelog-plugin',
    version='0.0.1',
    author='SilentE',
    description='Generates a changelog for pages',
    long_description=long_description,
    url='https://github.com/silentEAG/mkdocs-changelog-plugin',
    license='MIT',
    python_requires='>=3.5',
    install_requires=[
        'mkdocs>=1'
    ],
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    entry_points={
        'mkdocs.plugins': [
            'changelog = mkdocs_changelog_plugin:ChangelogPlugin'
        ]
    },
    include_package_data=True,
    package_data={
        'mkdocs_changelog_plugin': [
            'templates/*.html',
            'css/*.css'
        ]
    }
)