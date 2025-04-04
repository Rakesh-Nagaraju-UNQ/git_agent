"""
Git operations module for handling Git-related operations.
"""

import os
import git
import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

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

class MergeStrategy(Enum):
    """Available merge strategies."""
    RECURSIVE = 'recursive'
    OURS = 'ours'
    THEIRS = 'theirs'
    RESOLVE = 'resolve'
    OCTOPUS = 'octopus'

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
    
    def pull_code(self, branch: str = 'main') -> Dict[str, Any]:
        """
        Pull latest changes from remote repository with conflict detection.
        
        Args:
            branch (str): Branch to pull from
            
        Returns:
            Dict[str, Any]: Operation result with conflict information if any
        """
        try:
            origin = self.repo.remotes.origin
            result = origin.pull(branch)
            
            # Check for conflicts
            conflicts = self._check_for_conflicts()
            if conflicts:
                logger.warning(f"Merge conflicts detected in files: {conflicts}")
                return {
                    'success': False,
                    'error': 'Merge conflicts detected',
                    'conflicts': conflicts
                }
            
            logger.info(f"Successfully pulled latest changes from {branch}")
            return {'success': True, 'message': f'Successfully pulled from {branch}'}
        except git.exc.GitCommandError as e:
            if 'CONFLICT' in str(e):
                conflicts = self._check_for_conflicts()
                logger.error(f"Merge conflict detected during pull in files: {conflicts}")
                return {
                    'success': False,
                    'error': 'Merge conflict detected during pull',
                    'conflicts': conflicts
                }
            else:
                logger.error(f"Error pulling code: {str(e)}")
                return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during pull: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def merge_branch(self, base_branch: str = 'main', feature_branch: str = 'feature/new-branch',
                    strategy: MergeStrategy = MergeStrategy.RECURSIVE) -> Dict[str, Any]:
        """
        Merge a feature branch into base branch with conflict detection.
        
        Args:
            base_branch (str): Base branch to merge into
            feature_branch (str): Feature branch to merge from
            strategy (MergeStrategy): Merge strategy to use
            
        Returns:
            Dict[str, Any]: Operation result with conflict information if any
        """
        try:
            # Check if branches exist
            if base_branch not in self.repo.heads:
                return {'success': False, 'error': f'Base branch {base_branch} does not exist'}
            if feature_branch not in self.repo.heads:
                return {'success': False, 'error': f'Feature branch {feature_branch} does not exist'}
            
            # Switch to base branch
            self.repo.heads[base_branch].checkout()
            
            # Perform merge
            self.repo.git.merge(
                feature_branch,
                no_commit=True,
                strategy=strategy.value
            )
            
            # Check for conflicts
            conflicts = self._check_for_conflicts()
            if conflicts:
                logger.warning(f"Merge conflicts detected in files: {conflicts}")
                # Abort merge
                self.repo.git.merge('--abort')
                return {
                    'success': False,
                    'error': 'Merge conflicts detected',
                    'conflicts': conflicts
                }
            
            # Commit the merge
            self.repo.index.commit(f"Merge {feature_branch} into {base_branch}")
            
            logger.info(f"Successfully merged {feature_branch} into {base_branch}")
            return {'success': True, 'message': f'Successfully merged {feature_branch} into {base_branch}'}
        except git.exc.GitCommandError as e:
            if 'CONFLICT' in str(e):
                conflicts = self._check_for_conflicts()
                logger.error(f"Merge conflict detected during merge in files: {conflicts}")
                # Abort merge
                self.repo.git.merge('--abort')
                return {
                    'success': False,
                    'error': 'Merge conflict detected during merge',
                    'conflicts': conflicts
                }
            else:
                logger.error(f"Error merging branch: {str(e)}")
                return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during merge: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _check_for_conflicts(self) -> List[str]:
        """
        Check for merge conflicts in the repository.
        
        Returns:
            List[str]: List of files with conflicts
        """
        try:
            # Get unmerged files
            unmerged_blobs = self.repo.index.unmerged_blobs()
            conflict_files = []
            
            for path, list_of_blobs in unmerged_blobs.items():
                if any(blob.stage != 0 for blob in list_of_blobs):
                    conflict_files.append(path)
            
            return conflict_files
        except Exception as e:
            logger.error(f"Error checking for conflicts: {str(e)}")
            return []
    
    def resolve_conflicts(self, file_path: str, resolution: str) -> Dict[str, Any]:
        """
        Resolve conflicts in a specific file.
        
        Args:
            file_path (str): Path to the file with conflicts
            resolution (str): Resolution strategy ('ours', 'theirs', or 'both')
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if resolution not in ['ours', 'theirs', 'both']:
                return {'success': False, 'error': 'Invalid resolution strategy'}
            
            if resolution == 'ours':
                self.repo.git.checkout('--ours', file_path)
            elif resolution == 'theirs':
                self.repo.git.checkout('--theirs', file_path)
            elif resolution == 'both':
                # This would require custom conflict resolution logic
                pass
            
            # Mark the file as resolved
            self.repo.git.add(file_path)
            
            logger.info(f"Successfully resolved conflicts in {file_path}")
            return {'success': True, 'message': f'Resolved conflicts in {file_path}'}
        except Exception as e:
            logger.error(f"Error resolving conflicts: {str(e)}")
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
