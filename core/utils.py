import os
import shutil
import uuid  # Import the uuid library to create unique identifiers
from git import Repo, GitCommandError

def clone_repo(repo_url: str) -> str:
    """
    Clones a public GitHub repository to a new, unique temporary directory.
    
    This approach avoids file-locking issues on Windows by creating a
    unique directory for each run, rather than deleting and reusing one.

    Args:
        repo_url (str): The URL of the GitHub repository to clone.

    Returns:
        str: The local path to the newly cloned repository.

    Raises:
        ValueError: If the cloning process fails.
    """
    # Create a unique directory name using a UUID (Universally Unique Identifier)
    unique_id = str(uuid.uuid4())
    local_path = f"temp_repo_{unique_id}"
    
    print(f"Creating unique directory: {local_path}")
    
    try:
        print(f"Cloning repository from '{repo_url}'...")
        # Use GitPython to clone the repo into the new unique path
        Repo.clone_from(repo_url, local_path)
        print("Repository cloned successfully.")
        return local_path
    except GitCommandError as e:
        # If cloning fails for any reason, clean up the directory that was created
        if os.path.exists(local_path):
            shutil.rmtree(local_path, ignore_errors=True)
        raise ValueError(f"Failed to clone repository. Please check the URL. Error: {e}")