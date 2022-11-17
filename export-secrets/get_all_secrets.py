"""
This script runs a report on an organization to get the following information:
- Org level Action secrets
- Org level Dependabot secrets
- Repo level Action secrets
- Repo level Dependabot secrets

Environment Variables:
    API_TOKEN (str): GitHub API token.
    GHE_HOSTNAME (str): GitHub URL Slug (only needed if using GHES).
    organization (str): GitHub Organization name to run report against
"""

import csv
import os
from datetime import datetime

from dotenv import load_dotenv  # Import if you want to use .env file
from octopy_admin.graph.graph_client import GraphClient, GraphClientError
from octopy_admin.rest.rest_client import RestClient, RestClientError

load_dotenv()

# Create a new RestClient and GraphClient object and set the API_TOKEN and the GHE_HOSTNAME variables for GHES

github_rest = RestClient()
github_graph = GraphClient()
time = datetime.now()
organization = os.getenv("organization")


# Helper methods to generate report for the organization


def get_repos(org):
    """
    Get the list of repos.
    """
    try:
        results = github_graph.query.get_org_repos(org)
        repo_list = github_graph.query.results_to_list(results)
        return repo_list
    except GraphClientError as e:
        print(e)


def get_repos_with_visibility(org):
    """
    This module returns a generator that will yield a dictionary
    of all repositories in an organization.
    Attributes:
        org (str): The name of the Organization.
    """
    absolute_path = os.path.dirname(__file__)
    relative_path = "get-org-repo-list.graphql"
    full_path = os.path.join(absolute_path, relative_path)
    repo_query = github_graph._load_query(full_path)
    params = {"organization": org, "cursor": None}
    return github_graph.query._paginate_results(repo_query, params)


def list_repo_visibility(org):
    """
    Get the list of repos and include repository visibility.
    """
    try:
        results = get_repos_with_visibility(org)
        full_repo_list = github_graph.query.results_to_list(results)
        return full_repo_list
    except GraphClientError as e:
        print(e)


# Action specific secrets functions


def org_action_secrets(org):
    """
    List all organization Action secrets.
    """
    try:
        org_action_secret = github_rest.actions.list_organization_secrets(org)
        org_action_secret = org_action_secret.json()
        return org_action_secret
    except RestClientError as e:
        print(e)


def repo_action_secrets(org, repo):
    """
    Get the list of repo Action secrets.
    """
    try:
        repo_action_secret = github_rest.actions.list_repository_secrets(org, repo)
        repo_action_secret = repo_action_secret.json()
        return repo_action_secret
    except RestClientError as e:
        print(e)


def scoped_org_action_secrets(org, secret):
    """
    Get the list of repo Or secrets.
    """
    try:
        org_repo_action_secret = (
            github_rest.actions.list_selected_repositories_for_an_organization_secret(
                org, secret
            )
        )
        org_repo_action_secret = org_repo_action_secret.json()
        return org_repo_action_secret
    except RestClientError as e:
        print(e)


# Dependabot specific secrets functions


def org_dependabot_secrets(org):
    """
    List all organization Dependabot secrets.
    """
    try:
        org_dep_secret = github_rest.dependabot.list_organization_secrets(org)
        org_dep_secret = org_dep_secret.json()
        return org_dep_secret
    except RestClientError as e:
        print(e)


def repo_dependabot_secrets(org, repo):
    """
    Get the list of repo Dependabot secrets.
    """
    try:
        repo_dep_secret = github_rest.dependabot.list_repository_secrets(org, repo)
        repo_dep_secret = repo_dep_secret.json()
        return repo_dep_secret
    except RestClientError as e:
        print(e)


def scoped_org_dependabot_secrets(org, secret):
    """
    Get the list of repo Dependabot secrets.
    """
    try:
        org_repo_dep_secret = github_rest.dependabot.list_selected_repositories_for_an_organization_secret(
            org, secret
        )
        org_repo_dep_secret = org_repo_dep_secret.json()
        return org_repo_dep_secret
    except RestClientError as e:
        print(e)


# Codespaces specific secret functions


def org_codespaces_secrets(org):
    """
    List all organization Codespaces secrets.
    """
    try:
        org_cs_secret = github_rest.codespaces.list_organization_secrets(org)
        org_cs_secret = org_cs_secret.json()
        return org_cs_secret
    except RestClientError as e:
        print(e)


def repo_codespaces_secrets(org, repo):
    """
    Get the list of repo Codespaces secrets.
    """
    try:
        repo_cs_secret = github_rest.codespaces.list_repository_secrets(org, repo)
        repo_cs_secret = repo_cs_secret.json()
        return repo_cs_secret
    except RestClientError as e:
        print(e)


def scoped_org_codespace_secrets(org, secret):
    """
    Get the list of repo Codespaces secrets.
    """
    try:
        org_repo_cd_secret = github_rest.codespaces.list_selected_repositories_for_an_organization_secret(
            org, secret
        )
        org_repo_cd_secret = org_repo_cd_secret.json()
        return org_repo_cd_secret
    except RestClientError as e:
        print(e)


# Report Creation


def org_repo_secrets_report(org):
    """
    Generate a report for organization and repository levels list of secrets.
    Input: organization name.
    Output: CSV file with report.
    """
    print(f"Generating secrets report for the {org} organization...")
    report_time = datetime.now()
    report_time = time.isoformat("T", "seconds")
    org_repos = list_repo_visibility(org)
    secret_rows = []

    print("Gathering Action secrets.")
    org_action_secret_list = org_action_secrets(org)
    org_action_secret_list = org_action_secret_list["secrets"]
    for action_secret in org_action_secret_list:
        act_secret_name = action_secret["name"]
        act_secret_visibility = action_secret["visibility"]
        if act_secret_visibility == "selected":
            scoped_repo_list = scoped_org_action_secrets(org, act_secret_name)
            scoped_repo_list = scoped_repo_list["repositories"]
            for scope_list in scoped_repo_list:
                scope_repo_name = scope_list["name"]
                scope_repo_id = scope_list["id"]
                secret_rows.append(
                    [
                        "Organization",
                        "Action",
                        act_secret_name,
                        act_secret_visibility,
                        scope_repo_name,
                        scope_repo_id,
                    ]
                )
        elif act_secret_visibility == "private":
            private_repo_list = list_repo_visibility(org)
            for private_repo in private_repo_list:
                private_repo_name = private_repo["name"]
                private_repo_id = private_repo["databaseId"]
                private_repo_visibility = private_repo["visibility"]
            if (
                private_repo_visibility == "PRIVATE"
                or private_repo_visibility == "INTERNAL"
            ):
                secret_rows.append(
                    [
                        "Organization",
                        "Action",
                        act_secret_name,
                        act_secret_visibility,
                        private_repo_name,
                        private_repo_id,
                    ]
                )
        else:
            secret_rows.append(
                [
                    "Organization",
                    "Action",
                    act_secret_name,
                    act_secret_visibility,
                    "all_repositories",
                    "NA",
                ]
            )

    print("Gathering Dependabot secrets.")
    org_dependabot_secrets_list = org_dependabot_secrets(org)
    org_dependabot_secrets_list = org_dependabot_secrets_list["secrets"]
    for dependabot_secret in org_dependabot_secrets_list:
        dep_secret_name = dependabot_secret["name"]
        dep_secret_visibility = dependabot_secret["visibility"]
        if dep_secret_visibility == "selected":
            dep_scoped_repo_list = scoped_org_action_secrets(org, dep_secret_name)
            dep_scoped_repo_list = dep_scoped_repo_list["repositories"]
            for dep_scope_list in dep_scoped_repo_list:
                dep_scoped_repo_name = dep_scope_list["name"]
                dep_scoped_repo_id = dep_scope_list["id"]
                secret_rows.append(
                    [
                        "Organization",
                        "Dependabot",
                        dep_secret_name,
                        dep_secret_visibility,
                        dep_scoped_repo_name,
                        dep_scoped_repo_id,
                    ]
                )
        elif dep_secret_visibility == "private":
            dep_private_repo_list = list_repo_visibility(org)
            for dep_private_repo in dep_private_repo_list:
                dep_private_repo_name = dep_private_repo["name"]
                dep_private_repo_id = dep_private_repo["databaseId"]
                dep_private_repo_visibility = dep_private_repo["visibility"]
            if (
                dep_private_repo_visibility == "PUBLIC"
                or dep_private_repo_visibility == "INTERNAL"
            ):
                secret_rows.append(
                    [
                        "Organization",
                        "Dependabot",
                        dep_secret_name,
                        dep_secret_visibility,
                        dep_private_repo_name,
                        dep_private_repo_id,
                    ]
                )
        else:
            secret_rows.append(
                [
                    "Organization",
                    "Dependabot",
                    dep_secret_name,
                    dep_secret_visibility,
                    "all_repositories",
                    "NA",
                ]
            )

    print("Gathering Codespaces secrets.")
    org_codespace_secrets_list = org_codespaces_secrets(org)
    org_codespace_secrets_list = org_codespace_secrets_list["secrets"]
    for codespace_secret in org_codespace_secrets_list:
        codespace_secret_name = codespace_secret["name"]
        codespace_secret_visibility = codespace_secret["visibility"]
        if codespace_secret_visibility == "selected":
            codespace_scoped_repo_list = scoped_org_codespace_secrets(
                org, codespace_secret_name
            )
            codespace_scoped_repo_list = codespace_scoped_repo_list["repositories"]
            for codespace_scope_list in codespace_scoped_repo_list:
                codespace_scoped_repo_name = codespace_scope_list["name"]
                codespace_scoped_repo_id = codespace_scope_list["id"]
                secret_rows.append(
                    [
                        "Organization",
                        "Codespaces",
                        codespace_secret_name,
                        codespace_secret_visibility,
                        codespace_scoped_repo_name,
                        codespace_scoped_repo_id,
                    ]
                )
        elif codespace_secret_visibility == "private":
            codespace_private_repo_list = list_repo_visibility(org)
            for codespace_private_repo in codespace_private_repo_list:
                codespace_private_repo_name = codespace_private_repo["name"]
                codespace_private_repo_id = codespace_private_repo["databaseId"]
                codespace_private_repo_visibility = codespace_private_repo["visibility"]
            if (
                codespace_private_repo_visibility == "PUBLIC"
                or codespace_private_repo_visibility == "INTERNAL"
            ):
                secret_rows.append(
                    [
                        "Organization",
                        "Codespaces",
                        codespace_secret_name,
                        codespace_secret_visibility,
                        codespace_private_repo_name,
                        codespace_private_repo_id,
                    ]
                )
        else:
            secret_rows.append(
                [
                    "Organization",
                    "Codespaces",
                    codespace_secret_name,
                    codespace_secret_visibility,
                    "all_repositories",
                    "NA",
                ]
            )

    print("Gathering repository specific secrets.")
    for org_repo in org_repos:
        repo_name = org_repo["name"]
        repo_id = org_repo["databaseId"]
        repo_action_secret_list = repo_action_secrets(org, repo_name)
        if repo_action_secret_list is not None:
            repo_action_secret_list = repo_action_secret_list["secrets"]
            for repo_action_secret in repo_action_secret_list:
                repo_action_secret_name = repo_action_secret["name"]
                secret_rows.append(
                    [
                        "Repository",
                        "Action",
                        repo_action_secret_name,
                        "repo",
                        repo_name,
                        repo_id,
                    ]
                )
        repo_dependabot_secrets_list = repo_dependabot_secrets(org, repo_name)
        if repo_dependabot_secrets_list is not None:
            repo_dependabot_secrets_list = repo_dependabot_secrets_list["secrets"]
            for repo_dep_secret in repo_dependabot_secrets_list:
                repo_dep_secret_name = repo_dep_secret["name"]
                secret_rows.append(
                    [
                        "Repository",
                        "Dependabot",
                        repo_dep_secret_name,
                        "repo",
                        repo_name,
                        repo_id,
                    ]
                )
        repo_codespace_secrets_list = repo_codespaces_secrets(org, repo_name)
        if repo_codespace_secrets_list is not None:
            repo_codespace_secrets_list = repo_codespace_secrets_list["secrets"]
            for repo_codespace_secret in repo_codespace_secrets_list:
                repo_codespace_secret_name = repo_codespace_secret["name"]
                secret_rows.append(
                    [
                        "Repository",
                        "Codespaces",
                        repo_codespace_secret_name,
                        "repo",
                        repo_name,
                        repo_id,
                    ]
                )

    with open(
        f"{report_time}-{org}-organization-secrets-report.csv", "w", newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "SecretLevel",
                "SecretType",
                "SecretName",
                "SecretAccess",
                "RepositoryName",
                "RepositoryID",
            ]
        )
        writer.writerows(secret_rows)


org_repo_secrets_report(organization)
