import requests
import dateutil.parser

from requests.auth import HTTPBasicAuth

from server_api.models import Server


def GetAllAuthors():
    servers = Server.objects.all()
    result = []
    for server in servers:
        resp = requests.get(f"{server.server_address}authors", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        result += resp.json()["items"]

    return result


def GetAllPost():
    servers = Server.objects.all()
    result = []

    for server in servers:
        authors = requests.get(f"{server.server_address}authors", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        for author in authors.json()["items"]:
            posts = requests.get(f"{server.server_address}authors/{author['id'][-36:]}/posts", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
            result += posts.json()["items"]

    result.sort(key=lambda p: dateutil.parser.isoparse(p["published"]), reverse=True)
    return result

