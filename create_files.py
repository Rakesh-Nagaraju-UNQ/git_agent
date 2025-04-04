import os

# Create src directory if it doesn't exist
os.makedirs('src', exist_ok=True)

# Create __init__.py
init_content = '''"""
Git Agent package initialization.
"""

from .git_operations import GitOperations
from .github_api import GitHubAPI

__all__ = ["GitOperations", "GitHubAPI"]
'''

with open('src/__init__.py', 'w', encoding='utf-8') as f:
    f.write(init_content)

# Create git_operations.py
git_ops_content = '''"""
Git operations module for handling Git-related operations.
"""

import os
import git
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/git_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GitOperations:
    """Class to handle Git operations."""
    
    def __init__(self, repo_path: str):
        """
        Initialize GitOperations with repository path.
        
        Args:
            repo_path (str): Path to the Git repository
        """
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
            logger.info(f"Successfully initialized Git repository at {repo_path}")
        except git.InvalidGitRepositoryError:
            logger.error(f"Invalid Git repository at {repo_path}")
            raise
    
    def pull_code(self) -> Dict[str, Any]:
        """
        Pull latest changes from remote repository.
        
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            self.repo.git.pull()
            logger.info("Successfully pulled latest changes")
            return {'success': True, 'message': 'Successfully pulled latest changes'}
        except Exception as e:
            logger.error(f"Error pulling code: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """
        Create and switch to a new branch.
        
        Args:
            branch_name (str): Name of the new branch
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            # Create and switch to new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            logger.info(f"Successfully created and switched to branch: {branch_name}")
            return {'success': True, 'message': f'Successfully created branch: {branch_name}'}
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def push_code(self, branch: Optional[str] = None, commit_message: str = 'Update') -> Dict[str, Any]:
        """
        Push changes to remote repository.
        
        Args:
            branch (str, optional): Branch to push to
            commit_message (str): Commit message
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            # Add all changes
            self.repo.git.add('.')
            
            # Commit changes
            self.repo.index.commit(commit_message)
            
            # Push changes
            if branch:
                self.repo.git.push('origin', branch)
            else:
                self.repo.git.push()
            
            logger.info("Successfully pushed changes")
            return {'success': True, 'message': 'Successfully pushed changes'}
        except Exception as e:
            logger.error(f"Error pushing code: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def stash_changes(self) -> Dict[str, Any]:
        """
        Stash current changes.
        
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            self.repo.git.stash()
            logger.info("Successfully stashed changes")
            return {'success': True, 'message': 'Successfully stashed changes'}
        except Exception as e:
            logger.error(f"Error stashing changes: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def apply_stash(self) -> Dict[str, Any]:
        """
        Apply most recent stash.
        
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            self.repo.git.stash('pop')
            logger.info("Successfully applied stash")
            return {'success': True, 'message': 'Successfully applied stash'}
        except Exception as e:
            logger.error(f"Error applying stash: {str(e)}")
            return {'success': False, 'error': str(e)}
'''

with open('src/git_operations.py', 'w', encoding='utf-8') as f:
    f.write(git_ops_content)

# Create github_api.py
github_api_content = '''"""
GitHub API module for interacting with GitHub repositories.
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/github_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GitHubAPI:
    """Class to handle GitHub API operations."""
    
    def __init__(self):
        """Initialize GitHubAPI with GitHub token."""
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            logger.error("GitHub token not found in environment variables")
            raise ValueError("GitHub token not found in environment variables")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        logger.info("Successfully initialized GitHub API")
    
    def get_repo_info(self, repo_name: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            
        Returns:
            Dict[str, Any]: Repository information
        """
        try:
            url = f"{self.base_url}/repos/{repo_name}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Successfully retrieved repository info for {repo_name}")
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_pr(self, repo_name: str, base_branch: str, feature_branch: str,
                 title: str, body: str) -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            base_branch (str): Base branch to merge into
            feature_branch (str): Feature branch with changes
            title (str): Pull request title
            body (str): Pull request description
            
        Returns:
            Dict[str, Any]: Pull request creation result
        """
        try:
            url = f"{self.base_url}/repos/{repo_name}/pulls"
            data = {
                'title': title,
                'body': body,
                'head': feature_branch,
                'base': base_branch
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Successfully created PR in {repo_name}")
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating PR: {str(e)}")
            return {'success': False, 'error': str(e)}
'''

with open('src/github_api.py', 'w', encoding='utf-8') as f:
    f.write(github_api_content)

# Create test_operations.py
test_content = '''"""
Test script to verify Git and GitHub operations.
"""

import os
from src.git_operations import GitOperations
from src.github_api import GitHubAPI

def test_git_operations():
    """Test Git operations."""
    print("\\n=== Testing Git Operations ===")
    
    # Initialize Git operations with current directory
    current_dir = os.getcwd()
    git_ops = GitOperations(current_dir)
    
    # Test pull operation
    print("\\nTesting pull operation...")
    result = git_ops.pull_code()
    print(f"Pull result: {result}")
    
    # Test branch creation
    print("\\nTesting branch creation...")
    branch_name = 'test-feature-branch'  # Changed to use hyphens instead of slashes
    result = git_ops.create_branch(branch_name)
    print(f"Branch creation result: {result}")
    
    # Test push operation
    print("\\nTesting push operation...")
    result = git_ops.push_code(branch=branch_name, commit_message='Test commit')
    print(f"Push result: {result}")
    
    return branch_name  # Return the branch name for GitHub API test

def test_github_api(feature_branch):
    """Test GitHub API operations."""
    print("\\n=== Testing GitHub API Operations ===")
    
    # Initialize GitHub API
    github_api = GitHubAPI()
    
    # Get repository information
    print("\\nTesting repository info retrieval...")
    repo_name = "Rakesh-Nagaraju-UNQ/git_agent"
    owner = "Rakesh-Nagaraju-UNQ"
    result = github_api.get_repo_info(repo_name)
    print(f"Repository info: {result}")
    
    # Test PR creation
    print("\\nTesting PR creation...")
    result = github_api.create_pr(
        repo_name=repo_name,
        base_branch='main',
        feature_branch=f"{owner}:{feature_branch}",  # Include owner in branch name
        title='Test PR',
        body='This is a test pull request'
    )
    print(f"PR creation result: {result}")

if __name__ == "__main__":
    try:
        feature_branch = test_git_operations()
        test_github_api(feature_branch)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
'''

with open('test_operations.py', 'w', encoding='utf-8') as f:
    f.write(test_content)

# Create logs directory
os.makedirs('logs', exist_ok=True)

print("All files created successfully!") 