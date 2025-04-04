"""
GitHub API module for interacting with GitHub repositories.
"""

import os
import logging
import requests
import time
from typing import Dict, Any, Optional, List
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

    def get_pr_status(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """
        Get the status of a pull request including checks and reviews.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number
            
        Returns:
            Dict[str, Any]: Pull request status information
        """
        try:
            # Get PR details
            pr_url = f"{self.base_url}/repos/{repo_name}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Get check runs
            sha = pr_data['head']['sha']
            checks_url = f"{self.base_url}/repos/{repo_name}/commits/{sha}/check-runs"
            checks_response = requests.get(
                checks_url,
                headers={**self.headers, 'Accept': 'application/vnd.github.v3+json'}
            )
            checks_response.raise_for_status()
            checks_data = checks_response.json()
            
            # Get reviews
            reviews_url = f"{self.base_url}/repos/{repo_name}/pulls/{pr_number}/reviews"
            reviews_response = requests.get(reviews_url, headers=self.headers)
            reviews_response.raise_for_status()
            reviews_data = reviews_response.json()
            
            status = {
                'mergeable': pr_data.get('mergeable', False),
                'mergeable_state': pr_data.get('mergeable_state', 'unknown'),
                'checks': checks_data.get('check_runs', []),
                'reviews': reviews_data,
                'state': pr_data.get('state', 'unknown')
            }
            
            logger.info(f"Successfully retrieved PR status for #{pr_number} in {repo_name}")
            return {'success': True, 'data': status}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting PR status: {str(e)}")
            return {'success': False, 'error': str(e)}

    def is_pr_approved(self, repo_name: str, pr_number: int) -> bool:
        """
        Check if a pull request has been approved.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number
            
        Returns:
            bool: True if PR is approved, False otherwise
        """
        try:
            status = self.get_pr_status(repo_name, pr_number)
            if not status['success']:
                return False
                
            reviews = status['data']['reviews']
            approved = any(review['state'] == 'APPROVED' for review in reviews)
            return approved
        except Exception as e:
            logger.error(f"Error checking PR approval status: {str(e)}")
            return False

    def are_checks_passing(self, repo_name: str, pr_number: int) -> bool:
        """
        Check if all CI checks are passing for a pull request.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number
            
        Returns:
            bool: True if all checks are passing, False otherwise
        """
        try:
            status = self.get_pr_status(repo_name, pr_number)
            if not status['success']:
                return False
                
            checks = status['data']['checks']
            all_passing = all(check['conclusion'] == 'success' for check in checks)
            return all_passing
        except Exception as e:
            logger.error(f"Error checking CI status: {str(e)}")
            return False

    def merge_pr(self, repo_name: str, pr_number: int, merge_method: str = 'merge') -> Dict[str, Any]:
        """
        Merge a pull request if all conditions are met.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number
            merge_method (str): Merge method ('merge', 'squash', or 'rebase')
            
        Returns:
            Dict[str, Any]: Merge operation result
        """
        try:
            # Check if PR is approved and checks are passing
            if not self.is_pr_approved(repo_name, pr_number):
                return {'success': False, 'error': 'PR is not approved'}
            
            if not self.are_checks_passing(repo_name, pr_number):
                return {'success': False, 'error': 'CI checks are not passing'}
            
            # Get PR status to check if mergeable
            status = self.get_pr_status(repo_name, pr_number)
            if not status['success'] or not status['data']['mergeable']:
                return {'success': False, 'error': 'PR is not mergeable'}
            
            # Merge the PR
            url = f"{self.base_url}/repos/{repo_name}/pulls/{pr_number}/merge"
            data = {'merge_method': merge_method}
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Successfully merged PR #{pr_number} in {repo_name}")
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error merging PR: {str(e)}")
            return {'success': False, 'error': str(e)}

    def monitor_pr(self, repo_name: str, pr_number: int, check_interval: int = 60) -> Dict[str, Any]:
        """
        Monitor a PR until it's ready to merge or fails.
        
        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number
            check_interval (int): Time in seconds between status checks
            
        Returns:
            Dict[str, Any]: Final PR status
        """
        try:
            logger.info(f"Starting to monitor PR #{pr_number} in {repo_name}")
            
            while True:
                status = self.get_pr_status(repo_name, pr_number)
                if not status['success']:
                    return status
                
                pr_data = status['data']
                
                # Check if PR is closed or merged
                if pr_data['state'] == 'closed':
                    return {'success': True, 'data': {'status': 'closed'}}
                
                # Check if all conditions are met
                if (pr_data['mergeable'] and 
                    self.is_pr_approved(repo_name, pr_number) and 
                    self.are_checks_passing(repo_name, pr_number)):
                    return {'success': True, 'data': {'status': 'ready_to_merge'}}
                
                time.sleep(check_interval)
                
        except Exception as e:
            logger.error(f"Error monitoring PR: {str(e)}")
            return {'success': False, 'error': str(e)}
