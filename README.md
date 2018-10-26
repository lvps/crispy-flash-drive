# Crispy Flash Drive

Bake GNU/Linux distros (or any other iso file) on USB flash drives. A 
kind of [Freedom Toaster](https://en.wikipedia.org/wiki/Freedom_Toaster).

## Installation

Requires Python 3.

    virtualenv venv
    source venv/bin/activate
    python setup.py

Or, since apparently setup.py doesn't work, install `python-pyqt5`, `python-pysendfile` and `qt5-svg` (Arch Linux package names).
Or send a pull request with a working setup.py or anything similar, I'd really appreciate that.

To run:

    python cris.py
