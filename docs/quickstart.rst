==========
Quickstart
==========

## Setup API Key

Ensure your OpenAI API key is configured:

.. code-block:: console

   $ export OPENAI_API_KEY=your_api_key

Or add it to a `.env` file at the project root:

   OPENAI_API_KEY=your_api_key

## Creating a New Project

1. Create a new directory for your project:

   .. code-block:: console

      $ mkdir my-project

2. Inside the directory, create a file named `prompt` containing your instructions.

3. Run DevSeeker:

   .. code-block:: console

      $ devseeker my-project

Aliases: `ds`, `dste`

## Improving Existing Code

1. Navigate to an existing project directory.

2. Create or update the `prompt` file with your improvement instructions.

3. Run DevSeeker in improve mode:

   .. code-block:: console

      $ devseeker my-project -i

## Viewing Help

Run `devseeker --help` or `ds --help` to see all available options.
