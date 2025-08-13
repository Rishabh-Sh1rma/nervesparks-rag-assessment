import os
import shutil
from git import Repo, GitCommandError

def clone_repo(repo_url: str) -> str:
    """
    Clones a public GitHub repository to a temporary local directory.

    This function creates a temporary directory named 'temp_repo'. If this
    directory already exists, it is deleted to ensure a fresh clone. This is
    crucial for preventing errors from previous runs and making sure we are
    always working with the latest version of the repository for each new request.

    Args:
        repo_url (str): The URL of the GitHub repository to clone.

    Returns:
        str: The local path to the cloned repository if successful.

    Raises:
        ValueError: If the cloning process fails due to an invalid URL
                    or other Git-related errors.
    """
    # Define a consistent local path for the temporary repository
    local_path = "temp_repo"
    
    # Ensure a clean slate by removing the directory if it exists from a previous run
    if os.path.exists(local_path):
        print(f"Removing existing directory at '{local_path}'...")
        shutil.rmtree(local_path)
    
    try:
        print(f"Cloning repository from '{repo_url}'...")
        # Use GitPython to clone the repo into the specified local path
        Repo.clone_from(repo_url, local_path)
        print("Repository cloned successfully.")
        return local_path
    except GitCommandError as e:
        # This catches errors like invalid URLs, private repos, or network issues
        raise ValueError(f"Failed to clone repository. Please check the URL. Error: {e}")