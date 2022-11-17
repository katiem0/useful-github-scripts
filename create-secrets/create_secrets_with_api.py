"""
Script to create secrets for an organization and it's repositories.
"""

import csv
import json
import os
from base64 import b64encode

import apis
from dotenv import load_dotenv
from nacl import encoding, public

load_dotenv()

# Load environment variables:
NAME_PROPERTIES_FILE = os.getenv("SHARED_PROPERTIES_FILE")
ORGANIZATION_NAME = os.getenv("ORGANIZATION")
GITHUB_TOKEN = os.getenv("API_TOKEN")


def get_api_url():
    """
    Create the API_URL to use for API calls
    """
    hostname = os.environ.get("GHE_HOSTNAME")
    if os.environ.get("GHE_HOSTNAME") is None:
        rest_api_url = "https://api.github.com"
    else:
        rest_api_url = "https://" + hostname + "/api/v3"
    return rest_api_url


def get_headers():
    """
    Create the API_URL to use for API calls
    """
    api_token = os.environ.get("API_TOKEN")
    if os.environ.get("API_TOKEN") is None:
        return print("API_TOKEN environment variable is not set")
    headers = {"Authorization": f"Bearer {api_token}"}
    return headers


def create_properties_map(file_name: str):
    """
    Create key-value pairs with values loaded from CSV file
    """
    with open(file_name, newline="") as csvfile:
        properties_map = list(csv.DictReader(csvfile, delimiter=","))
    result_properties = json.dumps(properties_map)
    return result_properties


def encrypt(public_key: str, secret_value: str) -> str:
    """
    Encrypt a Unicode string using the public key.
    """
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def main():
    """
    Orchestrate calls necessary to populate organization and repo secrets based on a given file
    """

    base_api_url = get_api_url()
    api_headers = get_headers()

    # Retrieve unique action public key and key id pair for an organization:
    result_org_action_publickey = apis.actions.ActionsSecrets.get_org_public_key(
        base_api_url, api_headers, ORGANIZATION_NAME
    )
    action_org_public_key_id = result_org_action_publickey["key_id"]
    action_org_public_key_32bytes = result_org_action_publickey["key"]

    # Retrieve unique dependabot public key and key id pair for an organization:
    result_org_depd_publickey = apis.dependabot.DependabotSecrets.get_org_public_key(
        base_api_url, api_headers, ORGANIZATION_NAME
    )
    dependabot_org_public_key_id = result_org_depd_publickey["key_id"]
    dependabot_org_public_key_32bytes = result_org_depd_publickey["key"]

    # Load properties that will be added/updated in a wanted organization:
    map_properties = json.loads(create_properties_map(NAME_PROPERTIES_FILE))

    # Loop through properties loaded from CSV file to create/update GitHub Actions in an org:
    for row in map_properties:
        # Remove any white space:
        secret_level = row["SecretLevel"].replace(" ", "")
        secret_type = row["SecretType"].replace(" ", "")
        secret_name = row["SecretName"].replace(" ", "")
        secret_value = row["SecretValue"].replace(" ", "")
        secret_visibility = row["SecretAccess"].replace(" ", "")
        secret_repo = row["RepositoryName"]
        secret_repo_id = row["RepositoryID"]

        # Get encrypted value based on 32 bytes long public key from GitHub:
        action_org_encrypted_value = encrypt(
            action_org_public_key_32bytes, secret_value
        )
        dependabot_org_encrypted_value = encrypt(
            dependabot_org_public_key_32bytes, secret_value
        )

        # Create or update GitHub Actions secrets for all repositories:
        if secret_level == "Organization":
            if secret_visibility == "selected":
                if secret_type == "Action":
                    result = apis.actions.ActionsSecrets.update_org_secret_scoped(
                            base_api_url,
                            api_headers,
                            ORGANIZATION_NAME,
                            secret_name,
                            action_org_encrypted_value,
                            action_org_public_key_id,
                            secret_visibility,
                            secret_repo_id,
                    )
                else:
                    result = apis.dependabot.DependabotSecrets.update_org_secret_scoped(
                        base_api_url,
                        api_headers,
                        ORGANIZATION_NAME,
                        secret_name,
                        dependabot_org_encrypted_value,
                        dependabot_org_public_key_id,
                        secret_visibility,
                        secret_repo_id,
                    )
            else:
                if secret_type == "Action":
                    result = apis.actions.ActionsSecrets.update_org_secret(
                        base_api_url,
                        api_headers,
                        ORGANIZATION_NAME,
                        secret_name,
                        action_org_encrypted_value,
                        action_org_public_key_id,
                        secret_visibility,
                    )
                else:
                    result = apis.dependabot.DependabotSecrets.update_org_secret(
                        base_api_url,
                        api_headers,
                        ORGANIZATION_NAME,
                        secret_name,
                        dependabot_org_encrypted_value,
                        dependabot_org_public_key_id,
                        secret_visibility,
                    )

        elif secret_level == "Repository":
            # Retrieve unique action public key and key id pair for an organization:
            result_repo_action_publickey = (
                apis.actions.ActionsSecrets.get_repo_public_key(
                    base_api_url, api_headers, ORGANIZATION_NAME, secret_repo
                )
            )
            action_repo_public_key_id = result_repo_action_publickey["key_id"]
            action_repo_public_key_32bytes = result_repo_action_publickey["key"]

            # Retrieve unique dependabot public key and key id pair for an organization:
            result_repo_depd_publickey = (
                apis.dependabot.DependabotSecrets.get_repo_public_key(
                    base_api_url, api_headers, ORGANIZATION_NAME, secret_repo
                )
            )
            dependabot_repo_public_key_id = result_repo_depd_publickey["key_id"]
            dependabot_repo_public_key_32bytes = result_repo_depd_publickey["key"]

            action_repo_encrypted_value = encrypt(
                action_repo_public_key_32bytes, secret_value
            )
            dependabot_repo_encrypted_value = encrypt(
                dependabot_repo_public_key_32bytes, secret_value
            )
            if secret_type == "Action":
                result = apis.actions.ActionsSecrets.update_repo_secret(
                    base_api_url,
                    api_headers,
                    ORGANIZATION_NAME,
                    secret_repo,
                    secret_name,
                    action_repo_encrypted_value,
                    action_repo_public_key_id,
                )
            else:
                result = apis.dependabot.DependabotSecrets.update_repo_secret(
                    base_api_url,
                    api_headers,
                    ORGANIZATION_NAME,
                    secret_repo,
                    secret_name,
                    dependabot_repo_encrypted_value,
                    dependabot_repo_public_key_id,
                )

        else:
            print(f"There was an issue with secret {secret_name}")

        # Declare messages to print:
        message = ""

        # If a new GitHub Actions value got created:
        if result.status_code == 201:
            message = "Successfully created a new value for " + secret_name
        # If an existing GitHub Actions value got updated:
        elif result.status_code == 204:
            message = "Successfully updated an existing value for " + secret_name
        # If call fails of whatever reason:
        else:
            message = (
                "Hmm. Creating or updating a property named '"
                + secret_name
                + "' failed with a following status code : "
                + str(result.status_code)
            )
        print(message)


# Call main function:
if __name__ == "__main__":
    main()
