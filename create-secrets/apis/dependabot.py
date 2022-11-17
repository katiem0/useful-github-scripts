"""
Endpoints to manage Dependabot using the REST API.
"""
# pylint: disable=too-many-arguments, too-many-public-methods, too-many-lines, duplicate-code, no-self-argument

import requests


class DependabotSecrets:
    """
    Endpoints to manage Dependabot using the REST API.
    """

    def get_org_public_key(api_url, headers, org: str):
        """
        Get unique 32 bytes public key from GitHub Dependabot
        """
        org_public_key_url = f"{api_url}/orgs/{org}/dependabot/secrets/public-key"

        result = requests.get(org_public_key_url, headers=headers)
        return result.json()

    def get_repo_public_key(api_url, headers, org: str, repo: str):
        """
        Get unique 32 bytes public key from GitHub Dependabot
        """
        repo_public_key_url = (
            f"{api_url}/repos/{org}/{repo}/dependabot/secrets/public-key"
        )

        result = requests.get(repo_public_key_url, headers=headers)
        return result.json()

    def update_org_secret_scoped(
        api_url,
        headers,
        org: str,
        secret_name: str,
        encrypted_value: str,
        key_id: str,
        visibility: str,
        repo: str,
    ):
        """
        Update or create GitHub Dependabot secrets for an organization, scoped to a repo
        """
        repo_to_strings = list(map(str, repo.split(";")))
        data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id,
            "visibility": visibility,
            "selected_repository_ids": repo_to_strings,
        }
        org_update_secret_url = f"{api_url}/orgs/{org}/dependabot/secrets/{secret_name}"

        result = requests.put(org_update_secret_url, headers=headers, json=data)
        return result

    def update_org_secret(
        api_url,
        headers,
        org: str,
        secret_name: str,
        encrypted_value: str,
        key_id: str,
        visibility: str,
    ):
        """
        Update or create GitHub Dependabot secrets for an organization
        """
        data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id,
            "visibility": visibility,
        }
        org_update_secret_url = f"{api_url}/orgs/{org}/dependabot/secrets/{secret_name}"

        result = requests.put(org_update_secret_url, headers=headers, json=data)
        return result

    def update_repo_secret(
        api_url,
        headers,
        org: str,
        repo: str,
        secret_name: str,
        encrypted_value: str,
        key_id: str,
    ):
        """
        Update or create GitHub Dependabot secrets for a repository
        """
        data = {"encrypted_value": encrypted_value, "key_id": key_id}
        repo_update_secret_url = (
            f"{api_url}/repos/{org}/{repo}/dependabot/secrets/{secret_name}"
        )

        result = requests.put(repo_update_secret_url, headers=headers, json=data)
        return result
