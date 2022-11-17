# Create or update Secrets for an Organization and its Repositories

> **Warning**
> The main purpose of this script is to provide a workaround solution to manage non-sensitive properties in an automated way. Using this script can be very risky if you use this to manage sensitive secrets.

## File Structures


| File/directory path | What it is |
| ---- | ---------- |
| [`create_secrets_with_api.py`](/tools/scripts/create-secrets/create_secrets_with_api.py) | Python file that creates Action and Dependabot secrets at the organization and repository level |
| [`requirements.txt`](/tools/scripts/create-secrets/requirements.txt) | Python dependencies file |
| [`SAMPLE-shared-properties.csv`](/tools/scripts/create-secrets/SAMPLE-shared-properties.csv) | Sample `csv` structure to be read in by script |
| [`apis` directory](/tools/scripts/create-secrets/apis/) | Directory containing helper methods to call GitHub's REST API |


## Prerequisites

The following prerequisites are required to successfully run [`create_secrets_with_api.py`](/tools/scripts/create-secrets/create_secrets_with_api.py):

- You have an administrator permission to the organization(s) that you want to apply scripts
- An `API_TOKEN` environment variable scoped to:
  - `admin:org`
  - full `repo` access
- A `GHE_HOSTNAME` environment variable containing GitHub URL Slug (only needed if using GHES).
- An `ORGANIZATION` environment variable set to the Organization that all secrets will created in.
- The `SHARED_PROPERTIES_FILE` pointing to your secrets `csv` file (i.e.`shared-properties.csv`)
- The `apis` directory cloned in the same location as the `create_secrets_with_api.py`

> Note: This script can only write secrets to 1 organization at one time due to the encryption of a secret value, using the organization's `secrets/public-key` API endpoints for [actions](https://docs.github.com/en/rest/actions/secrets#get-an-organization-public-key) and [dependabot](https://docs.github.com/en/rest/dependabot/secrets#get-an-organization-public-key).

## Getting Started

### Shared Properties File

The `shared-properties.csv` file should be a CSV file using the `,` delimiter, comprised of the following information:

- `SecretLevel`
  - Specification of where secret should be created. Accepted values:
    - `Organization`
    - `Repository`
- `SecretType`
  - Specification of what type of secret should be created. Accepted values:
    - `Action`
    - `Dependabot`
- `SecretName`
  - The name of the secret to be created
- `SecretValue`
  - The unencrypted value of the secret to be added. This value is encrypted using the PAT provided before created from the API
- `SecretAccess`
  - Only used when the `SecretLevel = Organization`. This determines the repository access for a secret. Accepted values are:
    - `all`
    - `private`
    - `selected`
- `RepositoryName`
  - When the `SecretLevel = Organization` and `SecretAccess = selected`, this determines the repository names that the secret will be scoped to.
    - **This should be a string of names separated by `;`. (i.e. `migration-testing2;migration-testing`)**
  - When the `SecretLevel = Repository`, this is the name of the repository that the secret will be created under.
    - **This should only be 1 repository name**. If a secret is added to more than one repository at the **repository** level, it should be created as a separate line in the `shared-properties.csv` file.
- `RepositoryID`
  - Only used when the `SecretLevel = Organization` and `SecretAccess = selected`. This is the IDs of the repositories associated to the `RepositoryName` that the secret will be scoped to.
    - **This should be a string of IDs separated by `;`. (i.e. `514401003,501806768`)**

#### Install Required Dependencies

Run the following command to install required dependencies from `requirements.txt`

```sh
pip install -r requirements.txt
```

#### Run Python script to create or to update GitHub Actions secret

Run the following command to run Python script that will create or update GitHub Secrets in the specified organization and/or repositories:

```sh
python create_secrets_with_api.py
```

