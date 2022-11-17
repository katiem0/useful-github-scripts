# Organization and Repository Secrets Export

The script [`get_all_secrets.py`](get_all_secrets.py) utilizes GitHub's GraphQL and REST APIs to collect the following for an organization:

- Organization level Actions secrets
  - If applicable, the repositories that the secret is scoped to
- Organization level Dependabot secrets
  - If applicable, the repositories that the secret is scoped to
- Organization level Codespaces secrets
  - If applicable, the repositories that the secret is scoped to
- Repository level Action secrets
- Repository level Dependabot secrets
- Repository level Codespaces secrets

## Requirements

To run the script, the following is required:

- An `API_TOKEN` environment variable scoped to:
  - `admin:org`
  - full `repo` access
- A `GHE_HOSTNAME` environment variable containing GitHub URL Slug (only needed if using GHES).
- An `organization` environment variable set to the org wanting to extract secrets from.
- GraphQL query [`get-org-repo-list.graphql`](get-org-repo-list.graphql) in same directory where `get_all_secrets.py` exists


### Install Required Dependencies

Run the following command to install required dependencies from `requirements.txt`

```sh
pip install -r requirements.txt
```

### Run Python script to create or to update GitHub Actions secret

Run the following command to run Python script that will get all GitHub Secrets in the specified organization and/or repositories:

```sh
python get_all_secrets.py
```
