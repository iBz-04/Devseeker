# devseeker

[![PyPI version](https://img.shields.io/pypi/v/devseeker)](https://pypi.org/project/devseeker)

**devseeker is an CLI coding agent for generating and improving code through prompts**

## Installation

### Stable release

```sh
pip install devseeker
```

### Development installation

```sh
git clone https://github.com/iBz-04/devseeker.git
cd devseeker
poetry install
poetry shell
```

## Configuration

devseeker requires an OpenAI API key. Set it as an environment variable or in a `.env` file:

```sh
export OPENAI_API_KEY=your_api_key
```

or create a `.env` file:

```
OPENAI_API_KEY=your_api_key
```

## Usage

### Creating a new project

1. Create an empty directory for your project.
2. Inside the directory, create a file named `prompt` containing your instructions.
3. Run:

```sh
devseeker projects/my-new-project
```

### Improving existing code

```sh
devseeker projects/my-existing-project -i
```

### Benchmarking AI agents

```sh
bench run --help
```

## Commands

- `devseeker` (alias `ds`, `dste`) runs the main CLI application.
- `bench` runs benchmarks on AI agents.


- Windows users can refer to [WINDOWS_README.md](WINDOWS_README.md).

## Contributing

Contributions are welcome! 

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
