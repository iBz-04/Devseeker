<div align="center">
   <h2>Devseeker</h2>
</div>

<p align="center">
  <img src="https://res.cloudinary.com/diekemzs9/image/upload/v1746009112/extension_icon_1024px_jedbgf.png" alt="Seeker-o1 Logo" width="170"/>
</p>

<div align="center">
   <p><b>DevSeeker is a coding agent inspired by claude code and codex</b></p>
</div>




 [![PyPI version](https://img.shields.io/pypi/v/devseeker)](https://pypi.org/project/devseeker)




**devseeker can :**
- manage code files and folders
- Create and edit code on command 
- Store code in short-term memory
- review code changes
- run code files 
- calculate token usage
- offer multiple coding modes
- support wide range of ai models


## a little demo

https://github.com/user-attachments/assets/9b095f14-f376-429f-85e3-4fe42522cec4

**rare video of me losing a little game devseeker made :(**

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Operational Modes](#operational-modes)
- [CLI Options Reference](#cli-options-reference)
- [Environment Variables](#environment-variables)
- [Using Alternative Models](#using-alternative-models)
- [Project Configuration](#project-configuration)
- [File Selection](#file-selection)
- [Troubleshooting](#troubleshooting)
- [Windows-Specific Instructions](#windows-specific-instructions)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Via pip (Recommended)

```sh
pip install devseeker
```

### Development Installation

```sh
git clone https://github.com/iBz-04/devseeker.git
cd devseeker
poetry install
poetry env activate
```

## Configuration

DevSeeker requires an OpenAI API key. You can set it in three ways:

### 1. Environment variable

```sh
export OPENAI_API_KEY=your_api_key
```

### 2. .env file

Create a `.env` file in your project directory:

```
OPENAI_API_KEY=your_api_key
```

### 3. Custom configuration

For advanced configuration, create a `devseeker.toml` file in your project:

```toml
[run]
build = "npm run build"
test = "npm run test"
lint = "quick-lint-js"

[paths]
base = "./src"  # base directory to operate in
```

## Basic Usage

### Creating a New Project

1. Create an empty directory for your project
2. Inside the directory, create a file named `prompt` containing your instructions
3. Run DevSeeker:

```sh
devseeker projects/my-new-project
```

When you run this command, DevSeeker will:
- Present a welcome interface
- Read your prompt (or ask for one if not found)
- Generate code files based on your description
- Create an entrypoint file for running the project
- Ask if you want to execute the generated code

### Improving Existing Code

```sh
devseeker projects/my-existing-project -i
```

When you run DevSeeker in improve mode with the `-i` flag, it provides an interactive terminal UI that allows you to:

1. Describe how you want to improve your application through natural language prompts
2. Select which files should be modified (through an interactive file selection interface)
3. Review proposed changes in a diff view (showing what will be added/removed)
4. Accept or reject the changes before they're applied to your codebase

You can also use the `--skip-file-selection` or `-s` flag to bypass the interactive file selection:

```sh
devseeker projects/my-existing-project -i -s
```

## Operational Modes

DevSeeker supports several operational modes that change how it processes your prompts and generates code:

### Standard Mode (Default)

Generates complete projects following your prompt.

```sh
devseeker projects/my-project
```

### Improve Mode

Modifies existing code according to your instructions.

```sh
devseeker projects/my-project -i
```

### Clarify Mode

Discusses specifications with you before implementing them.

```sh
devseeker projects/my-project -c
```

### Lite Mode

Generates code using only your main prompt, without additional steps.

```sh
devseeker projects/my-project -l
```

### Self-Heal Mode

Automatically fixes code when it fails during execution.

```sh
devseeker projects/my-project -sh
```

## CLI Options Reference

DevSeeker offers numerous command-line options to customize its behavior:

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--model`, | `-m` | gpt-4o | The AI model to use |
| `--temperature` | `-t` | 0.1 | Controls randomness in outputs (0.0-1.0) |
| `--improve` | `-i` | False | Improves existing project |
| `--lite` | `-l` | False | Runs using only the main prompt |
| `--clarify` | `-c` | False | Discusses specifications before implementation |
| `--self-heal` | `-sh` | False | Auto-fixes failing code |
| `--azure` | `-a` | "" | Azure OpenAI endpoint URL |
| `--use-custom-preprompts` | | False | Uses custom prompts from project workspace |
| `--llm-via-clipboard` | | False | Uses clipboard for AI communication |
| `--verbose` | `-v` | False | Enables verbose logging |
| `--debug` | `-d` | False | Enables debug mode |
| `--prompt_file` | | "prompt" | Path to text file with prompt |
| `--entrypoint_prompt` | | "" | Path to file with entrypoint requirements |
| `--image_directory` | | "" | Path to folder with images |
| `--use_cache` | | False | Caches LLM responses to save tokens |
| `--skip-file-selection` | `-s` | False | Skips interactive file selection in improve mode |
| `--no_execution` | | False | Runs setup without calling LLM or writing code |
| `--sysinfo` | | False | Outputs system information for debugging |
| `--diff_timeout` | | 3 | Timeout for diff regexp searches |
| `--help` | `-h` | | Shows help information |

### Common Command Examples

```sh
# Basic usage - create a project from prompt
devseeker projects/my-project

# Create a project with a specific model
devseeker projects/my-project -m gpt-4-turbo

# Improve an existing project
devseeker projects/my-existing-project -i

# Improve a project with higher temperature for more creative outputs
devseeker projects/my-project -i -t 0.5

# Clarify requirements before implementation
devseeker projects/my-project -c

# Use lite mode for faster generation
devseeker projects/my-project -l

# Enable self-healing for auto-fixing code
devseeker projects/my-project -sh

# Use Azure OpenAI service
devseeker projects/my-project --azure https://<your-resource-name>.openai.azure.com

# Display help information
devseeker --help

# Display system information for troubleshooting
devseeker --sysinfo

# Skip file selection in improve mode
devseeker projects/my-project -i -s

# Use a specific prompt file
devseeker projects/my-project --prompt_file custom_prompt.txt

# Use images in your prompt
devseeker projects/my-project --image_directory images/

# Use custom preprompts
devseeker projects/my-project --use-custom-preprompts

# Enable verbose logging
devseeker projects/my-project -v
```

## Environment Variables

DevSeeker recognizes these environment variables:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `MODEL_NAME` | Default model to use (e.g., "gpt-4o") |
| `OPENAI_API_BASE` | Alternative API endpoint |
| `LOCAL_MODEL` | Set to "true" when using local models |
| `EDITOR` | Your preferred text editor |
| `LANGCHAIN_WANDB_TRACING` | Enable W&B tracing (set to "true") |
| `WANDB_API_KEY` | Weights & Biases API key |

## Using Alternative Models

### Local Models with llama.cpp

```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-your_local_key"
export MODEL_NAME="CodeLlama"
export LOCAL_MODEL=true
```

### Azure OpenAI

```bash
devseeker --azure https://<your-resource-name>.openai.azure.com my-project
```

See [docs/open_models.md](docs/open_models.md) for detailed instructions.

## Project Configuration

DevSeeker can be configured with a `devseeker.toml` file in your project root:

```toml
[run]
build = "npm run build"
test = "npm run test"
lint = "quick-lint-js"

[paths]
base = "./frontend"  # base directory for monorepos
src = "./src"        # source directory for context

[devseeker-app]      # used for devseeker.app integration
project_id = "..."
```

## File Selection

When improving code, DevSeeker needs to know which files to include in its context. The file selection process:

1. DevSeeker scans your project directory
2. Creates a TOML file with file paths
3. Opens this file in your text editor
4. You uncomment lines for files you want to include
5. Save and close the file to continue

The selection interface supports:
- Color-coded file types
- Intelligent defaults based on language
- Filtering of common directories like `node_modules`

## Troubleshooting

### Common Issues

#### API Key Not Found
```
Error: OpenAI API key not found
```
Solution: Set your `OPENAI_API_KEY` as described in Configuration.

#### Token Limit Exceeded
```
Error: This model's maximum context length is exceeded
```
Solution: Select fewer files in improve mode or use a model with higher token limits.

#### Execution Errors
If generated code fails to run, try:
- Using self-heal mode: `devseeker path/to/project -sh`
- Checking dependency installation
- Inspecting generated logs in the project's `.devseeker/logs` directory

## Windows-Specific Instructions

Windows users should consult [WINDOWS_README.md](WINDOWS_README.md) for platform-specific details.

Key differences:
- Use `set` instead of `export` for environment variables
- Path separators use backslashes
- Some commands may require PowerShell

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
