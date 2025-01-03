import requests
import csv

# Replace with your GitHub Personal Access Token
GITHUB_TOKEN = 'your_github_token_here'
# Replace with the target organization name
ORG_NAME = 'apache'

def get_repos(org_name):
    """Fetch all repositories for the given organization."""
    url = f'https://api.github.com/orgs/{org_name}/repos'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    params = {'per_page': 100}  # Adjust as needed; GitHub API paginates results
    repos = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        repos.extend(response.json())
        # Check for pagination
        url = response.links.get('next', {}).get('url')
    return repos

def get_repo_languages(repo_full_name):
    """Fetch the languages used in the repository."""
    url = f'https://api.github.com/repos/{repo_full_name}/languages'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_commit_count(repo_full_name):
    """Fetch the total number of commits in the repository."""
    url = f'https://api.github.com/repos/{repo_full_name}/commits?per_page=1'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # Extract the 'last' page number from the 'Link' header
    if 'Link' in response.headers:
        links = response.headers['Link']
        for link in links.split(','):
            if 'rel="last"' in link:
                # Extract the page number from the URL
                last_page_url = link.split(';')[0].strip('<> ')
                last_page_number = int(last_page_url.split('page=')[-1])
                return last_page_number
    # If there's no 'Link' header, there's only one page
    return len(response.json())

def main():
    repos = get_repos(ORG_NAME)
    # Open the CSV file for writing
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Repository Name', 'Repository URL', 'Java Usage (%)', 'Commit Count'])
        for repo in repos:
            languages = get_repo_languages(repo['full_name'])
            total_bytes = sum(languages.values())
            java_bytes = languages.get('Java', 0)
            if total_bytes > 0:
                java_usage_percent = (java_bytes / total_bytes) * 100
                if java_usage_percent >= 95:
                    commit_count = get_commit_count(repo['full_name'])
                    writer.writerow([repo['name'], repo['html_url'], f"{java_usage_percent:.2f}", commit_count])

if __name__ == '__main__':
    main()
