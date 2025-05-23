# Windows Users Setup

On Windows, to set API key do one of the following:
- `set OPENAI_API_KEY=[your api key]` on cmd
- `$env:OPENAI_API_KEY="[your api key]"` on powershell

## Full setup guide

Choose either **stable** or **development**.

For **stable** release:

Run `pip install devseeker` in the command line as an administrator

Or:

  1. Open your web browser and navigate to the Python Package Index (PyPI) website: <https://pypi.org/project/devseeker/>.
  2. On the PyPI page for the devseeker package, locate the "Download files" section. Here you'll find a list of available versions and their corresponding download links.
  3. Identify the version of devseeker you want to install and click on the associated download link. This will download the package file (usually a .tar.gz or .whl file) to your computer.
  4. Once the package file is downloaded, open your Python development environment or IDE.
  5. In your Python development environment, look for an option to install packages or manage dependencies. The exact location and terminology may vary depending on your IDE. For example, in PyCharm, you can go to "File" > "Settings" > "Project: \<project-name>" > "Python Interpreter" to manage packages.
  6. In the package management interface, you should see a list of installed packages. Look for an option to add or install a new package.
  7. Click on the "Add Package" or "Install Package" button.
  8. In the package installation dialog, choose the option to install from a file or from a local source.
  9. Browse and select the downloaded devseeker package file from your computer.

For **development**:

- `git clone git@github.com:devseeker-org/devseeker.git`
- `cd devseeker`
- `poetry install`
- `poetry env activate` to activate the virtual environment

### Setup

With an api key from OpenAI:

Run `set OPENAI_API_KEY=[your API key]` in the command line

Or:

  1. In the Start Menu, type to search for "Environment Variables" and click on "Edit the system environment variables".
  2. In the System Properties window, click on the "Environment Variables" button.
  3. In the Environment Variables window, you'll see two sections: User variables and System variables.
  4. To set a user-specific environment variable, select the "New" button under the User variables section.
  5. To set a system-wide environment variable, select the "New" button under the System variables section.
  6. Enter the variable name "OPENAI_API_KEY" in the "Variable name" field.
  7. Enter the variable value (e.g., your API key) in the "Variable value" field.
  8. Click "OK" to save the changes.
  9. Close any open command prompt or application windows and reopen them for the changes to take effect.

Now you can use `%OPENAI_API_KEY%` when prompted to input your key.

### Run

YOU CAN RUN THE CLI WITH `poetry run devseeker`

- Create an empty folder. If inside the repo, you can:
  - Run `xcopy /E projects\example projects\my-new-project` in the command line or `Copy-Item -Path "projects\example" -Destination "projects\my-new-project" -Recurse`
  - Or hold CTRL and drag the folder down to create a copy, then rename to fit your project
- Fill in the `prompt` file in your new folder with your command
- `devseeker projects/my-new-project` or `poetry run devseeker projects/my-new-project`
  - (Note, `devseeker --help` lets you see all available options. For example `--steps use_feedback` lets you improve/fix code in a project)
- Also ` devseeker projects/my-existing-project -i` or  `devseeker projects/my-existing-project -improve`

  NB: If you want to create a game you might want to install pygame `pip install pygame`

### Results

- Check the generated files in `projects/my-new-project/workspace`
