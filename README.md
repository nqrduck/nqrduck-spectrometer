# NQRduck Module: nqrduck-spectrometer

A module for the [nqrduck](https://github.com/nqrduck/nqrduck) project. This module is used as a base module for implementing different spectrometers. It provides the basic functionality for controlling a spectrometer and programming pulse sequences.

## Installation

### Requirements
Dependencies are handled via the pyproject.toml file.

### Setup
To install the module you need the NQRduck core. You can find the installation instructions for the NQRduck core [here](https://github.com/nqrduck/nqrduck).

Ideally you should install the module in a virtual environment. You can create a virtual environment by running the following command in the terminal:
```bash
python -m venv nqrduck
# Activate the virtual environment
. nqrduck/bin/activate
```

You can install this module and the dependencies by running the following command in the terminal while the virtual environment is activated and you are in the root directory of this module:
```bash
pip install .
```

## Usage
Examples for implementation of submodules can be found in the following repositories:

- [nqrduck-spectrometer-limenqr](https://github.com/nqrduck/nqrduck-spectrometer-limenqr) A module used for magnetic resonance experiments with the LimeSDR (USB or Mini 2.0).
- [nqrduck-spectrometer-simulator](https://github.com/nqrduck/nqrduck-spectrometer-simulator) A module used for simulating magnetic resonance experiments.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contributing
If you're interested in contributing to the project, start by checking out our [nqrduck-module template](https://github.com/nqrduck/nqrduck-module). To contribute to existing modules, please first open an issue in the respective module repository to discuss your ideas or report bugs.
