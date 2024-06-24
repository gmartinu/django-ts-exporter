from setuptools import setup, find_packages

setup(
    name="django-ts-exporter",
    version="0.4.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django>=3.0", "djangorestframework>=3.11"],
    entry_points={
        "console_scripts": [
            "django-ts-exporter=django_ts_exporter.exporter:main",
        ],
    },
    author="Gabriel Martinusso",
    author_email="gabrielbramos@outlook.com",
    description="Export Django models and serializers to TypeScript interfaces",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gmartinu/django-ts-exporter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
