"""
GitHub API client for accessing repository contents.
Uses PyGithub library for GitHub API interactions.
"""
import os
from typing import Optional, List, Dict, Any
from github import Github, GithubException


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client."""
        self.token = token
        self.github = Github(token) if token else Github()
    
    async def get_repository_structure(
        self, 
        owner: str, 
        repo: str, 
        path: str = "/", 
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get structure of files and directories at a given path."""
        try:
            # Get repository
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            
            # Get contents at specified path
            if branch:
                contents = repo_obj.get_contents(path, ref=branch)
            else:
                contents = repo_obj.get_contents(path)
            
            # Handle single file vs directory
            if isinstance(contents, list):
                items = []
                for item in contents:
                    item_data = {
                        "name": item.name,
                        "path": item.path,
                        "type": "dir" if item.type == "dir" else "file",
                        "size": None
                    }
                    
                    # Add size for files only
                    if item.type == "file":
                        item_data["size"] = item.size
                    
                    items.append(item_data)
                
                return {
                    "path": path,
                    "items": items
                }
            else:
                # Single file at path - return as directory with one item
                return {
                    "path": path,
                    "items": [{
                        "name": contents.name,
                        "path": contents.path,
                        "type": "file",
                        "size": contents.size
                    }]
                }
                
        except GithubException as e:
            raise Exception(f"GitHub API error: {e}")
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        file_path: str, 
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content of a specific file."""
        # Get repository
        repo_obj = self.github.get_repo(f"{owner}/{repo}")
        
        # Get file content
        if branch:
            file_content = repo_obj.get_contents(file_path, ref=branch)
        else:
            file_content = repo_obj.get_contents(file_path)

        # Error if directory
        if isinstance(file_content, list):
            raise ValueError("Cannot get directory content")
        
        # Decode content based on encoding
        content_str = ""
        
        if hasattr(file_content, 'decoded_content'):
            # For text files with decoded_content attribute
            decoded_bytes = getattr(file_content, 'decoded_content')
            if decoded_bytes is not None:
                content_str = decoded_bytes.decode('utf-8')
            else:
                content_str = ""
        
        elif hasattr(file_content, 'content'):
            # For files with base64 encoded content attribute  
            import base64
            try:
                decoded_bytes = base64.b64decode(getattr(file_content, 'content'))
                content_str = decoded_bytes.decode('utf-8')
            except Exception as decode_error:
                content_str = f"[Binary or unsupported encoding - size: {file_content.size} bytes]"
        
        return {
            "path": file_path,
            "content": content_str,
            "size": file_content.size,
            "encoding": "utf-8"
        }
    
    async def test_connection(self) -> bool:
        """Test connection to GitHub API."""
        try:
            # Simple API call to test connectivity and rate limits  
            rate_limit = self.github.get_rate_limit()
            
            # Check if we have remaining requests
            if rate_limit.core.remaining > 0:
                return True
            else:
                # Rate limit exhausted, but connection is still valid
                return True
                
        except Exception as e:
            return False
    
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information."""
        repo_obj = self.github.get_repo(f"{owner}/{repo}")
        
        return {
            "name": repo_obj.name,
            "full_name": repo_obj.full_name,
            "description": repo_obj.description,
            "owner": repo_obj.owner.login,
            "private": repo_obj.private,
            "fork": repo_obj.fork,
            "created_at": repo_obj.created_at.isoformat() if repo_obj.created_at else None,
            "updated_at": repo_obj.updated_at.isoformat() if repo_obj.updated_at else None,
            "pushed_at": repo_obj.pushed_at.isoformat() if repo_obj.pushed_at else None,
            "size": repo_obj.size,
            "stargazers_count": repo_obj.stargazers_count,
            "watchers_count": repo_obj.watchers_count,
            "forks_count": repo_obj.forks_count,
            "open_issues_count": repo_obj.open_issues_count,
            "default_branch": repo_obj.default_branch,
            "language": repo_obj.language,
            "topics": list(repo_obj.topics) if hasattr(repo_obj, 'topics') else [],
        }
    
    async def search_code(
        self, 
        query: str, 
        owner: Optional[str] = None, 
        repo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for code in GitHub repositories."""
        # Build search query
        search_query = query
        
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        # Perform search
        results = self.github.search_code(search_query)
        
        # Format results
        formatted_results = []
        for result in results[:50]:  # Limit to 50 results for performance
            formatted_results.append({
                "name": result.name,
                "path": result.path,
                "repository": result.repository.full_name,
                "url": result.html_url,
                "score": result.score if hasattr(result, 'score') else None,
                "size": result.size if hasattr(result, 'size') else None,
                "language": result.repository.language if hasattr(result.repository, 'language') else None,
            })
        
        return formatted_results