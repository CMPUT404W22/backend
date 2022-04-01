import json

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


def GetAllPosts():
    servers = Server.objects.all()
    result = []

    for server in servers:
        authors = requests.get(f"{server.server_address}authors", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        for author in authors.json()["items"]:
            if server.server_address == "https://squawker-cmput404.herokuapp.com/api/":
                posts = requests.get(f"{server.server_address}authors/{author['id'][-36:]}/posts", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
                result += posts.json()["posts"]
            else:
                posts = requests.get(f"{server.server_address}authors/{author['id'][-36:]}/posts", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
                result += posts.json()["items"]

    result.sort(key=lambda p: dateutil.parser.isoparse(p["published"]), reverse=True)
    return result


def GetAllPostComments(server, author, post):
    comments = requests.get(f"{server.server_address}authors/{author}/posts/{post}/comments", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return comments.json()


def GetAllPostLikes(server, author, post):
    comments = requests.get(f"{server.server_address}authors/{author}/posts/{post}/likes",auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return comments.json()

def SendLike(server, author, user_id, post_id):

    data = {
        "summary": author["displayName"] + " likes your post",
        "type": "like",
        "author": author,
        "object": f"{server.server_address}authors/{user_id}/posts/{post_id}"
    }

    headers = {'Content-type': 'application/json'}
    like = requests.post(f"{server.server_address}authors/{user_id}/inbox", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]), data=json.dumps(data), headers=headers)

    return like.status_code

def SendContentToInbox(server, author_id, content):
    return requests.post(f"{server.server_address}authors/{author_id}/inbox",
        auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]),
        data=content)
        