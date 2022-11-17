"""
This script runs a report on the enterprise environment to get the following information:
- list of orgs
- list of repos
- last commit per repo
- number of branches per repo
- list of forks per repo
- forks of forks per repo


Environment Variables:
    API_TOKEN (str): GitHub API token with `read:enterprise`, `read:org` and `repo` applied scopes.
    GHE_HOSTNAME (str): GitHub URL Slug (only needed if using GHES).
    ENTERPRISE (str): GitHub Enterprise name to run report against
"""

import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv  # Import if you want to use .env file
from octopy_admin.graph.graph_client import GraphClient, GraphClientError
from octopy_admin.rest.rest_client import RestClient, RestClientError

load_dotenv()


# Create a new RestClient and GraphClient object and set the API_TOKEN and the GHE_HOSTNAME variables for GHES


github_rest = RestClient()
graph_github = GraphClient()
time = datetime.now()
enterprise_name = os.getenv("ENTERPRISE")


# Helper methods to generate report for enterprise


def get_orgs(enterprise):
    """
    Get the list of orgs.
    """
    try:
        results = graph_github.query.get_enterprise_orgs(enterprise)
        org_list = graph_github.query.results_to_list(results)
        return org_list
    except GraphClientError as e:
        print(e)


def get_repos(org):
    """
    Get the list of repos.
    """
    try:
        results = graph_github.query.get_org_repos(org)
        repo_list = graph_github.query.results_to_list(results)
        return repo_list
    except GraphClientError as e:
        print(e)


def get_last_commit(org, name):
    """
    Get the last commit for a repo.
    """
    api_token = os.environ.get("API_TOKEN")
    if os.environ.get("API_TOKEN") is None:
        raise RestClientError("API_TOKEN environment variable is not set")
    headers = {"Authorization": f"Bearer {api_token}"}
    hostname = os.environ.get("GHE_HOSTNAME")
    if os.environ.get("GHE_HOSTNAME") is None:
        rest_api_url = "https://api.github.com"
    else:
        rest_api_url = "https://" + hostname + "/api/v3"
    url = rest_api_url + f"/repos/{org}/{name}/commits"
    commit_response = requests.request(
        method="get",
        url=url,
        headers=headers,
        timeout=10,
    )
    if not commit_response:
        last_commit = []
    else:
        commit_response = commit_response.json()
        last_commit = commit_response[0]["commit"]["author"]
    return last_commit


def get_branch_count(org, name):
    """
    Get the number of branches for a repo.
    """
    try:
        branches = github_rest.repos.list_branches(org, name)
        num_branches = len(branches.json())
        return num_branches
    except RestClientError as e:
        print(e)


def get_fork_list(org, name):
    """
    Get the list of forked repos for a repo and children forks.
    """
    try:
        fork_raw = github_rest.repos.list_forks(
            org,
            name,
            params={
                "page": "1",
                "per_page": "100",
            },
        )
        fork_pages = fork_raw.json()
        while fork_raw.links.get("next") != fork_raw.links.get("last"):
            url = fork_raw.links.get("next").get("url")
            fork_raw = github_rest._execute("GET", url)
            raw = fork_raw.json()
            fork_pages.extend(raw)
        fork_list = []
        for index, fork in enumerate(fork_pages):
            fork_name = fork["name"]
            fork_full_name = fork["full_name"]
            owner_name = fork["owner"]["login"]
            fork_count = fork["forks_count"]
            fork_list.append(
                {
                    "name": fork_name,
                    "full_name": fork_full_name,
                    "owner_login": owner_name,
                    "fork_count": fork_count,
                    "fork_children_info": [],
                }
            )
            if fork_count > 0:
                new_fork_url = fork["forks_url"]
                api_token = os.environ.get("API_TOKEN")
                headers = {"Authorization": f"Bearer {api_token}"}
                fork_forks = requests.request(
                    method="get",
                    url=new_fork_url,
                    headers=headers,
                    timeout=10,
                    params={
                        "page": "1",
                        "per_page": "100",
                    },
                )
                if fork_forks:
                    fork_forks_response = fork_forks.json()
                    for fork_child in fork_forks_response:
                        fork_fork_name = fork_child["name"]
                        fork_fork_full_name = fork_child["full_name"]
                        fork_owner_name = fork_child["owner"]["login"]
                        fork_fork_count = fork_child["forks_count"]
                        fork_list[index]["fork_children_info"].append(
                            {
                                "name": fork_fork_name,
                                "full_name": fork_fork_full_name,
                                "owner_login": fork_owner_name,
                                "fork_count": fork_fork_count,
                            }
                        )
        return fork_list
    except RestClientError as e:
        print(e)


def generate_report(enterprise):
    """
    Generate a report for an enterprise.
    Input: enterprise name.
    Output: JSON file with report.
    """
    print(f"Generating report for the {enterprise} enterprise...")
    org_list = get_orgs(enterprise)
    print(f"Found {len(org_list)} organizations in the {enterprise} enterprise.")
    org_repo_forks = []
    for index, org in enumerate(org_list):
        org_name = org["login"]
        org_repo = get_repos(org_name)
        org_repo_forks.append({"org_name": org_name, "repos": []})
        for repo in org_repo:
            repo_name = repo["name"]
            repo_updated_at = repo["updatedAt"]
            repo_last_commit = get_last_commit(org_name, repo_name)
            repo_branch_count = get_branch_count(org_name, repo_name)
            if not repo_branch_count:
                repo_branch_count = []
            repo_fork_list = get_fork_list(org_name, repo_name)
            org_repo_forks[index]["repos"].append(
                {
                    "name": repo_name,
                    "updated_at": repo_updated_at,
                    "last_commit": repo_last_commit,
                    "num_branches": repo_branch_count,
                    "forks": repo_fork_list,
                }
            )
    report_time = datetime.now()
    report_time = time.isoformat("T", "seconds")
    with open(
        f"{report_time}-{enterprise}-enterprise-network-report.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(org_repo_forks, f, ensure_ascii=False, indent=4)


generate_report(enterprise_name)
