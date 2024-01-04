import csv
import os
import tarfile
import json

# Get environment variables
ARCHIVE_PATH = os.getenv('ARCHIVE_PATH')

tarfiles = tarfile.open(ARCHIVE_PATH, "r:gz")
MAPPING_HEADER = ["login","name","email","url"]

with open("user-mapping.csv", "w") as new_file:
    # create user-mapping csv to write to
    csv_writer = csv.writer(new_file)
    csv_writer.writerow(MAPPING_HEADER)

    # iterate through tarfile to find users_*.json files
    for filename in tarfiles.getnames():
        if "users_" in filename:
            contents = json.loads(tarfiles.extractfile(filename).read())
            for row in contents:
                login = row["login"]
                name = row["name"]
                email = ""
                for emails in row["emails"]:
                    if emails["primary"]:
                        email = emails["address"]
                url = row["url"]
                csv_writer.writerow([login, name, email, url])
