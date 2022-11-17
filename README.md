# Useful GitHub Scripts

A collection of scripts to aid in solving a problem that GitHub users experience.

* Export Organization and Repository Secrets
* Create Organization and Repository Secrets
* Create Enterprise level Network Graph for all Organizations and Repositories

## Export Organization and Repository Secrets

A [script](/export-secrets/README.md) that utilizes GitHub's GraphQL and REST APIs to collect the following for an organization:

- Organization level Actions secrets
  - If applicable, the repositories that the secret is scoped to
- Organization level Dependabot secrets
  - If applicable, the repositories that the secret is scoped to
- Organization level Codespaces secrets
  - If applicable, the repositories that the secret is scoped to
- Repository level Action secrets
- Repository level Dependabot secrets
- Repository level Codespaces secrets

## Create Organization and Repository Secrets

A [script](/create-secrets/README.md) that utilizes GitHub's GraphQL and REST APIs to **create** the following for an organization:

- Organization level Actions secrets
- Organization level Dependabot secrets
- Repository level Action secrets
- Repository level Dependabot secrets

## Create Enterprise level Network Graph for all Organizations and Repositories

A [script](/enterprise-network-graph/enterprise_repo_networks.py) that runs a report on an Enterprise to get the following information:
- List of Organizations
- List of Repositories
- Last Commit per Repository
- Number of Branches per Repository
- List of forks per Repository
- Identifies Forks of Forks per Repository
