"""
Endpoints to manage Dependabot using the REST API.
"""
# pylint: disable=too-many-arguments, too-many-public-methods, too-many-lines, duplicate-code, line-too-long, no-self-argument
import requests


class DependabotSecrets:
    """
    Endpoints to manage Dependabot using the REST API.
    """

    def get_org_public_key(api_url, headers, org: str):
        """
        Get unique 32 bytes public key from GitHub Dependabot
        """
        try:
            ORG_PUBLIC_KEY_URL = f"{api_url}/orgs/{org}/dependabot/secrets/public-key"

            result = requests.get(ORG_PUBLIC_KEY_URL, headers=headers)
            return result.json()
        except requests.exceptions.HTTPError as err:
            print(err)

    def get_repo_public_key(api_url, headers, org: str, repo: str):
        """
        Get unique 32 bytes public key from GitHub Dependabot
        """
        try:
            ORG_PUBLIC_KEY_URL = (
                f"{api_url}/repos/{org}/{repo}/dependabot/secrets/public-key"
            )

            result = requests.get(ORG_PUBLIC_KEY_URL, headers=headers)
            return result.json()
        except requests.exceptions.HTTPError as err:
            print(err)

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
        try:
            repo_to_strings = list(map(str, repo.split(";")))
            data = {
                "encrypted_value": encrypted_value,
                "key_id": key_id,
                "visibility": visibility,
                "selected_repository_ids": repo_to_strings,
            }
            ORG_UPDATE_SECRET_URL = (
                f"{api_url}/orgs/{org}/dependabot/secrets/{secret_name}"
            )

            result = requests.put(ORG_UPDATE_SECRET_URL, headers=headers, json=data)
            return result
        except requests.exceptions.HTTPError as err:
            print(err)

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
        try:
            data = {
                "encrypted_value": encrypted_value,
                "key_id": key_id,
                "visibility": visibility,
            }
            ORG_UPDATE_SECRET_URL = (
                f"{api_url}/orgs/{org}/dependabot/secrets/{secret_name}"
            )

            result = requests.put(ORG_UPDATE_SECRET_URL, headers=headers, json=data)
            return result
        except requests.exceptions.HTTPError as err:
            print(err)

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
        try:
            data = {"encrypted_value": encrypted_value, "key_id": key_id}
            REPO_UPDATE_SECRET_URL = (
                f"{api_url}/repos/{org}/{repo}/dependabot/secrets/{secret_name}"
            )

            result = requests.put(REPO_UPDATE_SECRET_URL, headers=headers, json=data)
            return result
        except requests.exceptions.HTTPError as err:
            print(err)
