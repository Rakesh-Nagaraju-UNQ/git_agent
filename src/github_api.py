"""
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
