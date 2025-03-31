# Git Commit Gen

A command-line tool to automatically generate concise and informative commit messages following the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/) using the Google Gemini API.

## Features
- Analyzes staged Git changes (modified, added, and deleted files).
- Generates commit messages based on file diffs and changes.
- Ensures messages adhere to Conventional Commits format (e.g., `feat: add new feature`).
- Falls back to standard `git commit` if generation fails.

## Installation

Install the package via pip:

```bash
pip install git-commit-gen
```

### Prerequisites
- Python 3.8 or higher
- Git installed and configured
- A Google Gemini API key (see [Configuration](#configuration))

## Usage

Run the tool in a Git repository with staged changes:

```bash
git-commit-gen
```

You can pass additional Git commit options:

```bash
git-commit-gen --amend
git-commit-gen -v
```

The tool will:
1. Analyze your staged changes.
2. Generate a commit message using the Gemini API.
3. Warn if the message doesn't follow Conventional Commits.
4. Execute the commit with the generated message.

## Configuration

The tool requires a Google Gemini API key. Set it in a `.env` file in your working directory or as an environment variable:

### Using a `.env` file
Create a `.env` file in your project root:

```
GEMINI_API_KEY=your_api_key_here
```

### Using environment variables
Set the key in your shell:

```bash
export GEMINI_API_KEY=your_api_key_here
```

Optional environment variables:
- `GEMINI_MODEL`: Specify the Gemini model (default: `gemini-2.0-flash-001`).
- `MAX_DIFF_SIZE`: Maximum diff size to include in the prompt (default: `2000`).

## Example

1. Stage some changes:
   ```bash
   git add .
   ```

2. Run the tool:
   ```bash
   git-commit-gen
   ```

3. Output might look like:
   ```
   feat: implement user authentication
   ```

If the generated message doesn't follow Conventional Commits:
   ```
   Warning: Generated commit message may not follow Conventional Commits.
   It is recommended to review and adjust the message before committing.
   Proposed message: update readme file
   ```

## Development

### Project Structure
```
git_commit_gen/
├── git_commit_gen/
│   ├── __init__.py
│   └── git_commit_gen.py
├── pyproject.toml
└── README.md
```

### Build the Package
To build locally:
```bash
pip install hatchling build
python -m build
```

### Install Locally
```bash
pip install dist/git_commit_gen-0.1.0-py3-none-any.whl
```

## Contributing
Feel free to submit issues or pull requests on the [GitHub repository](https://github.com/Salnika/ai-commit-message)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Built with [Google Gemini API](https://developers.google.com/gemini).

