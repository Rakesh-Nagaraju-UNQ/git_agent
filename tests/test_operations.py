"""
Test script to verify Git and GitHub operations.
"""

import os
import sys
import time
import pytest
from src.git_operations import GitOperations, MergeStrategy
from src.github_api import GitHubAPI

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def test_merge_conflicts():
    """Test merge conflict detection and resolution."""
    print("\n=== Testing Merge Conflict Handling ===")
    
    # Initialize Git operations
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_ops = GitOperations(current_dir)
    
    # Create test branches
    timestamp = int(time.time())
    base_branch = f'base-branch-{timestamp}'
    feature_branch = f'feature-branch-{timestamp}'
    
    # Create and switch to base branch
    print("\nCreating base branch...")
    result = git_ops.create_branch(base_branch)
    assert result['success'], f"Failed to create base branch: {result.get('error')}"
    
    # Create a test file in base branch
    test_file = 'test_conflict.txt'
    with open(test_file, 'w') as f:
        f.write("Base branch content")
    
    # Commit changes in base branch
    result = git_ops.push_code(branch=base_branch, commit_message='Add test file')
    assert result['success'], f"Failed to commit in base branch: {result.get('error')}"
    
    # Create and switch to feature branch
    print("\nCreating feature branch...")
    result = git_ops.create_branch(feature_branch)
    assert result['success'], f"Failed to create feature branch: {result.get('error')}"
    
    # Modify the test file in feature branch
    with open(test_file, 'w') as f:
        f.write("Feature branch content")
    
    # Commit changes in feature branch
    result = git_ops.push_code(branch=feature_branch, commit_message='Modify test file')
    assert result['success'], f"Failed to commit in feature branch: {result.get('error')}"
    
    # Switch back to base branch and modify the same file
    print("\nModifying file in base branch...")
    result = git_ops.create_branch(base_branch)
    assert result['success'], f"Failed to switch to base branch: {result.get('error')}"
    
    with open(test_file, 'w') as f:
        f.write("Modified base branch content")
    
    # Commit changes in base branch
    result = git_ops.push_code(branch=base_branch, commit_message='Modify test file in base')
    assert result['success'], f"Failed to commit in base branch: {result.get('error')}"
    
    # Attempt to merge feature branch into base branch
    print("\nAttempting merge...")
    result = git_ops.merge_branch(
        base_branch=base_branch,
        feature_branch=feature_branch,
        strategy=MergeStrategy.RECURSIVE
    )
    
    # Check for conflicts
    if not result['success'] and 'conflicts' in result:
        print(f"Merge conflicts detected in files: {result['conflicts']}")
        
        # Test conflict resolution
        print("\nTesting conflict resolution...")
        for file_path in result['conflicts']:
            # Try resolving with 'ours' strategy
            resolution_result = git_ops.resolve_conflicts(file_path, 'ours')
            print(f"Resolution result for {file_path}: {resolution_result}")
            assert resolution_result['success'], f"Failed to resolve conflicts: {resolution_result.get('error')}"
    
    # Clean up test branches
    print("\nCleaning up test branches...")
    git_ops.repo.git.branch('-D', base_branch)
    git_ops.repo.git.branch('-D', feature_branch)
    
    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)

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
        test_merge_conflicts()
        test_github_api()
    except Exception as e:
        print(f"Error during testing: {str(e)}") 