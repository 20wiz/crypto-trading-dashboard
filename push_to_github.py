import os
import requests
import subprocess
import time

def create_github_repo():
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN not found in environment")
        return None
        
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': 'crypto-trading-dashboard',
        'description': 'A cryptocurrency trading dashboard with real-time charts, multiple strategies, and signal notifications',
        'private': False,
        'auto_init': False
    }
    
    try:
        response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
        
        if response.status_code == 201:
            return response.json()['clone_url']
        elif response.status_code == 422:  # Repository already exists
            # Get username from the token
            user_response = requests.get('https://api.github.com/user', headers=headers)
            if user_response.status_code == 200:
                username = user_response.json()['login']
                return f'https://github.com/{username}/crypto-trading-dashboard.git'
        print(f"Failed to create repository: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error creating repository: {str(e)}")
        return None

def setup_and_push(repo_url):
    try:
        # Configure git user (using generic values since this is a one-time push)
        subprocess.run(['git', 'config', '--global', 'user.email', 'replit@example.com'], check=True, capture_output=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Replit'], check=True, capture_output=True)
        
        # Initialize repository if needed
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        
        commands = [
            ['git', 'remote', 'remove', 'origin'],  # Remove existing origin if any
            ['git', 'remote', 'add', 'origin', repo_url],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'Initial commit: Cryptocurrency Trading Dashboard'],
            ['git', 'branch', '-M', 'main'],
            ['git', 'push', '-u', 'origin', 'main', '--force']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and 'nothing to commit' not in result.stderr:
                print(f"Error executing {' '.join(cmd)}: {result.stderr}")
                return False
            # Add small delay between commands
            time.sleep(1)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

# Main execution
repo_url = create_github_repo()
if repo_url:
    print(f"Repository URL: {repo_url}")
    if setup_and_push(repo_url):
        print("Successfully pushed code to GitHub")
        exit(0)
    else:
        print("Failed to push code to GitHub")
        exit(1)
else:
    print("Failed to create or find GitHub repository")
    exit(1)
