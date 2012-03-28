from distutils.core import setup

setup(name="pyline",
      version="0.1",
      description="command-line interaction toolkit",
      author="Ben Wolfson",
      author_email="wolfson@gmail.com",
      packages=["pyline"],
      package_dir={"pyline":"pyline"},
      long_description = open("README.rst").read(),
      classifiers = sorted([
          "License :: OSI Approved :: BSD License",
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python",
          "Natural Language :: English"]),
      )
          
