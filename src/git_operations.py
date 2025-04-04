"""
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
