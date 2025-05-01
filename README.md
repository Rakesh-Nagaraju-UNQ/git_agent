# Git Agent

A professional Python library for Git and GitHub operations management.

## Features

- Git repository operations (pull, push, branch management)
- GitHub API integration (PR creation, repository info)
- Robust error handling and logging
- Type hints and documentation

## Project Structure

```
git_agent/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── git_operations.py  # Git operations module
│   └── github_api.py      # GitHub API module
├── tests/                 # Test files
│   ├── __init__.py
│   └── test_operations.py
├── logs/                  # Log files
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rakesh-Nagaraju-UNQ/git_agent.git
cd git_agent
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your GitHub token
```

## Usage

```python
from src.git_operations import GitOperations
from src.github_api import GitHubAPI

# Initialize Git operations
git_ops = GitOperations("/path/to/repo")

# Create and switch to new branch
result = git_ops.create_branch("feature/new-branch")

# Push changes
result = git_ops.push_code(branch="feature/new-branch", commit_message="Add new feature")

# Create PR using GitHub API
github_api = GitHubAPI()
result = github_api.create_pr(
    repo_name="owner/repo",
    base_branch="main",
    feature_branch="feature/new-branch",
    title="New Feature",
    body="Implemented new feature"
)
```

## Development

1. Run tests:
```bash
python -m pytest tests/
```

2. Check logs:
```bash
tail -f logs/git_operations.log
tail -f logs/github_api.log
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 