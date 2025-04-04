"""
Test script to verify Git and GitHub operations.
"""

import os
import sys
import time

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.git_operations import GitOperations
from src.github_api import GitHubAPI

def test_git_operations():
    """Test Git operations."""
    print("\n=== Testing Git Operations ===")
    
    # Initialize Git operations with current directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_ops = GitOperations(current_dir)
    
    # Test pull operation
    print("\nTesting pull operation...")
    result = git_ops.pull_code()
    print(f"Pull result: {result}")
    
    # Test branch creation with timestamp to ensure uniqueness
    print("\nTesting branch creation...")
    timestamp = int(time.time())
    branch_name = f'test-branch-{timestamp}'
    result = git_ops.create_branch(branch_name)
    print(f"Branch creation result: {result}")
    
    # Test push operation
    print("\nTesting push operation...")
    result = git_ops.push_code(branch=branch_name, commit_message='Test commit')
    print(f"Push result: {result}")
    
    # Return the branch name for GitHub API test
    return branch_name

def test_github_api():
    """Test GitHub API operations."""
    print("\n=== Testing GitHub API Operations ===")
    
    # Initialize GitHub API
    github_api = GitHubAPI()
    
    # Get repository information
    print("\nTesting repository info retrieval...")
    repo_name = "Rakesh-Nagaraju-UNQ/git_agent"
    result = github_api.get_repo_info(repo_name)
    print(f"Repository info: {result}")
    
    # Create a test branch for PR
    timestamp = int(time.time())
    feature_branch = f'test-branch-{timestamp}'
    
    # Test PR creation
    print("\nTesting PR creation...")
    result = github_api.create_pr(
        repo_name=repo_name,
        base_branch='main',
        feature_branch=feature_branch,
        title='Test PR',
        body='This is a test pull request'
    )
    print(f"PR creation result: {result}")
    
    if result['success']:
        pr_number = result['data']['number']
        
        # Test PR status monitoring
        print("\nTesting PR status monitoring...")
        status = github_api.get_pr_status(repo_name, pr_number)
        print(f"PR status: {status}")
        
        # Test PR approval check
        print("\nTesting PR approval check...")
        is_approved = github_api.is_pr_approved(repo_name, pr_number)
        print(f"PR approved: {is_approved}")
        
        # Test CI checks status
        print("\nTesting CI checks status...")
        checks_passing = github_api.are_checks_passing(repo_name, pr_number)
        print(f"Checks passing: {checks_passing}")
        
        # Test PR monitoring
        print("\nTesting PR monitoring...")
        monitor_result = github_api.monitor_pr(repo_name, pr_number, check_interval=10)
        print(f"Monitor result: {monitor_result}")
        
        # Test PR merging
        if monitor_result['success'] and monitor_result['data']['status'] == 'ready_to_merge':
            print("\nTesting PR merging...")
            merge_result = github_api.merge_pr(repo_name, pr_number)
            print(f"Merge result: {merge_result}")

if __name__ == "__main__":
    try:
        test_git_operations()
        test_github_api()
    except Exception as e:
        print(f"Error during testing: {str(e)}") 