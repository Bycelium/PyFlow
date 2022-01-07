# PyFlow

[![Pytest badge](https://github.com/Bycelium/PyFlow/actions/workflows/python-tests.yml/badge.svg?branch=master)](https://github.com/MathisFederico/opencodeblocks/actions/workflows/python-tests.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9874915d70e440418447f371c4bd5061)](https://www.codacy.com/gh/Bycelium/PyFlow/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Bycelium/PyFlow&amp;utm_campaign=Badge_Grade)
[![Pylint badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FMathisFederico%2F00ce73155619a4544884ca6d251954b3%2Fraw%2Fopencodeblocks_pylint_badge.json)](https://github.com/MathisFederico/opencodeblocks/actions/workflows/python-pylint.yml)
[![Total coverage Codacy Badge](https://app.codacy.com/project/badge/Coverage/ddd03302fd7c4849b452959753bc0939)](https://www.codacy.com/gh/MathisFederico/opencodeblocks/dashboard?utm_source=github.com&utm_medium=referral&utm_content=MathisFederico/opencodeblocks&utm_campaign=Badge_Coverage)
[![Unit coverage badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FMathisFederico%2F00ce73155619a4544884ca6d251954b3%2Fraw%2Fopencodeblocks_unit_coverage_badge.json)](https://github.com/MathisFederico/opencodeblocks/actions/workflows/python-coverage.yml)
[![Integration coverage badge](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FMathisFederico%2F00ce73155619a4544884ca6d251954b3%2Fraw%2Fopencodeblocks_integration_coverage_badge.json)](https://github.com/MathisFederico/opencodeblocks/actions/workflows/python-coverage.yml)
[![Licence - GPLv3](https://img.shields.io/github/license/MathisFederico/Crafting?style=plastic)](https://www.gnu.org/licenses/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

PyFlow is an open-source graph-structured interactive Python development tool

Although for now Pyflow is in closed Beta and features are coming in bit by bit, stay tuned for the first release soon !

![](media/mnist_example.gif)

## Community

Join our [Discord](https://discord.gg/xZq8Tp4srd) to beta-test features, share your ideas, contribute or just to have a chat with us.

## Features

- Create blocks of code in which you can edit and run Python code

<p align="center">
  <img src="media/block_example.gif" width="400"/>
</p>

- Move and resize blocks on an infinite 2D plane

<p align="center">
  <img src="media/resize_example.gif" width="400"/>
</p>

- Link blocks to highlight dependencies, Pyflow will then automatically run your blocks in the correct order

<p align="center">
  <img src="media/flow_example.gif" width="400"/>
</p>

- Convert your Jupyter notebooks to Pyflow graphs and vice versa

<p align="center">
  <img src="media/notebook_example.gif" width="400"/>
</p>

## Installation

Make sure you have Python 3 installed. You can download it from [here](https://www.python.org/downloads/)

### Clone the repository

Using git:
```bash
git clone git@github.com:Bycelium/PyFlow.git
```

or using https:
```bash
git clone https://github.com/Bycelium/PyFlow.git
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run PyFlow !

```bash
python -m pyflow
```

## Contributing

If you are interested in contributing to the project, see [CONTRIBUTING.md](CONTRIBUTING.md).

You can also join our [Discord](https://discord.gg/xZq8Tp4srd) to get in touch with us.

## License

See [LICENSE](LICENSE)
