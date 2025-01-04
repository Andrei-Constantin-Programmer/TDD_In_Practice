import requests

from src.infrastructure import file_utils

class RepositoryFinder():
    APACHE_ORGANISATION = 'apache'

    def __init__(self, github_token):
        self.github_token = github_token

    def _get_repos(self, org_name, pagination = 100):
        """Fetch all repositories for the given organization."""
        url = f'https://api.github.com/orgs/{org_name}/repos'
        headers = {'Authorization': f'token {self.github_token}'}
        params = {'per_page': pagination}
        repos = []
        while url:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            repos.extend(response.json())
            url = response.links.get('next', {}).get('url')
        return repos

    def _get_repo_languages(self, repo_full_name):
        """Fetch the languages used in the repository."""
        url = f'https://api.github.com/repos/{repo_full_name}/languages'
        headers = {'Authorization': f'token {self.github_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {key.lower(): value for key, value in response.json().items()}

    def _get_commit_count(self, repo_full_name):
        """Fetch the total number of commits in the repository."""
        url = f'https://api.github.com/repos/{repo_full_name}/commits?per_page=1'
        headers = {'Authorization': f'token {self.github_token}'}
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

    def extract_repositories(self, organisation, pagination, language, maximum):
        repos = self._get_repos(organisation, pagination)[:maximum]
        print(f"Found {len(repos)} total repositories.")
        csv_contents = [['Repository Name', 'Repository URL', f'{language.title()} Usage (%)', 'Commit Count']]

        for repo in repos:
            try:
                languages = self._get_repo_languages(repo['full_name'])
                total_bytes = sum(languages.values())
                lang_bytes = languages.get(language, 0)
                if total_bytes > 0:
                    lang_usage_percent = (lang_bytes / total_bytes) * 100
                    if lang_usage_percent >= 90:
                        commit_count = self._get_commit_count(repo['full_name'])
                        csv_contents.append([repo['name'], repo['html_url'], f"{lang_usage_percent:.2f}", commit_count])
            except Exception as e:
                print(f"Could not perform analysis on repo {repo}: {e}")

        file_utils.write_csv(csv_contents, "repositories")
