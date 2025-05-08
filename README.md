# devseeker

[![GitHub Repo stars](https://img.shields.io/github/stars/devseeker-org/devseeker?style=social)](https://github.com/devseeker-org/devseeker)
[![Discord Follow](https://dcbadge.vercel.app/api/server/8tcDQ89Ej2?style=flat)](https://discord.gg/8tcDQ89Ej2)
[![License](https://img.shields.io/github/license/devseeker-org/devseeker)](https://github.com/devseeker-org/devseeker/blob/main/LICENSE)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/devseeker-org/devseeker)](https://github.com/devseeker-org/devseeker/issues)
![GitHub Release](https://img.shields.io/github/v/release/devseeker-org/devseeker)
[![Twitter Follow](https://img.shields.io/twitter/follow/antonosika?style=social)](https://twitter.com/antonosika)

The OG code genereation experimentation platform!

If you are looking for the evolution that is an opinionated, managed service – check out devseeker.app.

If you are looking for a well maintained hackable CLI for – check out aider.


devseeker lets you:
- Specify software in natural language
- Sit back and watch as an AI writes and executes the code
- Ask the AI to implement improvements

## Getting Started

### Install devseeker

For **stable** release:

- `python -m pip install devseeker`

For **development**:
- `git clone https://github.com/devseeker-org/devseeker.git`
- `cd devseeker`
- `poetry install`
- `poetry shell` to activate the virtual environment

We actively support Python 3.10 - 3.12. The last version to support Python 3.8 - 3.9 was [0.2.6](https://pypi.org/project/devseeker/0.2.6/).

### Setup API key

Choose **one** of:
- Export env variable (you can add this to .bashrc so that you don't have to do it each time you start the terminal)
    - `export OPENAI_API_KEY=[your api key]`
- .env file:
    - Create a copy of `.env.template` named `.env`
    - Add your OPENAI_API_KEY in .env
- Custom model:
    - See [docs](https://devseeker.readthedocs.io/en/latest/open_models.html), supports local model, azure, etc.

Check the [Windows README](./WINDOWS_README.md) for Windows usage.

**Other ways to run:**
- Do everything in your browser:
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/devseeker-org/devseeker/codespaces)

### Create new code (default usage)
- Create an empty folder for your project anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions
- Run `devseeker projects/my-new-project` with a relative path to your folder
  - For example: `devseeker projects/my-new-project` from the devseeker directory root with your new folder in `projects/`

### Improve existing code
- Locate a folder with code which you want to improve anywhere on your computer
- Create a file called `prompt` (no extension) inside your new folder and fill it with instructions for how you want to improve the code
- Run `devseeker projects/my-old-project -i` with a relative path to your folder
  - For example: `devseeker projects/my-old-project -i` from the devseeker directory root with your folder in `projects/`

### Benchmark custom agents
- devseeker installs the binary 'bench', which gives you a simple interface for benchmarking your own agent implementations against popular public datasets.
- The easiest way to get started with benchmarking is by checking out the [template](https://github.com/devseeker-org/gpte-bench-template) repo, which contains detailed instructions and an agent template.
- Currently supported benchmark:
  - [APPS](https://github.com/hendrycks/apps)
  - [MBPP](https://github.com/google-research/google-research/tree/master/mbpp)

The community has started work with different benchmarking initiatives, as described in [this Loom](https://www.loom.com/share/206805143fbb4302b5455a5329eaab17?sid=f689608f-8e49-44f7-b55f-4c81e9dc93e6) video.

### Research
Some of our community members have worked on different research briefs that could be taken further. See [this document](https://docs.google.com/document/d/1qmOj2DvdPc6syIAm8iISZFpfik26BYw7ZziD5c-9G0E/edit?usp=sharing) if you are interested.

## Terms
By running devseeker, you agree to our [terms](https://github.com/devseeker-org/devseeker/blob/main/TERMS_OF_USE.md).


## Relation to devseeker.app (GPT Engineer)
[devseeker.app](https://devseeker.app/) is a commercial project for the automatic generation of web apps.
It features a UI for non-technical users connected to a git-controlled codebase.
The devseeker.app team is actively supporting the open source community.


## Features

### Pre Prompts
You can specify the "identity" of the AI agent by overriding the `preprompts` folder with your own version of the `preprompts`. You can do so via the `--use-custom-preprompts` argument.

Editing the `preprompts` is how you make the agent remember things between projects.

### Vision

By default, devseeker expects text input via a `prompt` file. It can also accept image inputs for vision-capable models. This can be useful for adding UX or architecture diagrams as additional context for GPT Engineer. You can do this by specifying an image directory with the `—-image_directory` flag and setting a vision-capable model in the second CLI argument.

E.g. `devseeker projects/example-vision gpt-4-vision-preview --prompt_file prompt/text --image_directory prompt/images -i`

### Open source, local and alternative models

By default, devseeker supports OpenAI Models via the OpenAI API or Azure OpenAI API, as well as Anthropic models.

With a little extra setup, you can also run with open source models like WizardCoder. See the [documentation](https://devseeker.readthedocs.io/en/latest/open_models.html) for example instructions.

## Mission

The devseeker community mission is to **maintain tools that coding agent builders can use and facilitate collaboration in the open source community**.

If you are interested in contributing to this, we are interested in having you.

If you want to see our broader ambitions, check out the [roadmap](https://github.com/devseeker-org/devseeker/blob/main/ROADMAP.md), and join
[discord](https://discord.gg/8tcDQ89Ej2)
to learn how you can [contribute](.github/CONTRIBUTING.md) to it.

devseeker is [governed](https://github.com/devseeker-org/devseeker/blob/main/GOVERNANCE.md) by the [Contributor Covenant Code of Conduct](https://github.com/devseeker-org/devseeker/blob/main/CODE_OF_CONDUCT.md). All contributors are expected to uphold this code.


https://github.com/devseeker-org/devseeker/assets/4467025/40d0a9a8-82d0-4432-9376-136df0d57c99
