"""
Test script to verify Git and GitHub operations.
"""

import os
from src.git_operations import GitOperations
from src.github_api import GitHubAPI

def test_git_operations():
    """Test Git operations."""
    print("\n=== Testing Git Operations ===")
    
    # Initialize Git operations with current directory
    current_dir = os.getcwd()
    git_ops = GitOperations(current_dir)
    
    # Test pull operation
    print("\nTesting pull operation...")
    result = git_ops.pull_code()
    print(f"Pull result: {result}")
    
    # Test branch creation
    print("\nTesting branch creation...")
    branch_name = 'test-feature-branch'  # Changed to use hyphens instead of slashes
    result = git_ops.create_branch(branch_name)
    print(f"Branch creation result: {result}")
    
    # Test push operation
    print("\nTesting push operation...")
    result = git_ops.push_code(branch=branch_name, commit_message='Test commit')
    print(f"Push result: {result}")
    
    return branch_name  # Return the branch name for GitHub API test

def test_github_api(feature_branch):
    """Test GitHub API operations."""
    print("\n=== Testing GitHub API Operations ===")
    
    # Initialize GitHub API
    github_api = GitHubAPI()
    
    # Get repository information
    print("\nTesting repository info retrieval...")
    repo_name = "Rakesh-Nagaraju-UNQ/git_agent"
    owner = "Rakesh-Nagaraju-UNQ"
    result = github_api.get_repo_info(repo_name)
    print(f"Repository info: {result}")
    
    # Test PR creation
    print("\nTesting PR creation...")
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