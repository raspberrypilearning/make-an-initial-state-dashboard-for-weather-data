import os, json

credentials_file = os.path.join(os.path.dirname(__file__), "credentials.initialstate")
f = open(credentials_file, "r")
credentials = json.load(f)

print(credentials['ACCESS_KEY'])
