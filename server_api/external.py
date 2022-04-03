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


def GetAuthor(server, id):
    resp = requests.get(f"{server.server_address}author/{id}",
                        auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return resp.json()["items"]


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


def GetPost(server, author, post):
    posts = requests.get(f"{server.server_address}authors/{author}/posts/{post}",
                         auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))

    return posts.json()


def GetAllPostComments(server, author, post):
    comments = requests.get(f"{server.server_address}authors/{author}/posts/{post}/comments", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return comments.json()


def GetAllPostLikes(server, author, post):
    comments = requests.get(f"{server.server_address}authors/{author}/posts/{post}/likes",auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return comments.json()

def GetAllFollowers(server, author):
    followers = requests.get(f"{server.server_address}authors/{author}/followers", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return followers.json()

def CheckFollower(server, author, follower):
    follower_json = None
    if server.server_address == "https://psdt11.herokuapp.com/":
        follower = requests.get(f"{server.server_address}authors/{author}/followers/{follower}", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        follower_json = follower.json()["items"]
    elif server.server_address == "https://squawker-cmput404.herokuapp.com/api/":
        follower = requests.get(f"{server.server_address}authors/{author}/followers/{follower}", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        follower_json = follower.json()["detail"]
    elif server.server_address == "https://c404-social-distribution.herokuapp.com/service/":
        follower = requests.get(f"{server.server_address}authors/{author}/followers/{follower}", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
        follower_json = follower.json()
    
    return follower_json

def delete_follower(server, author_id, follower_id):
    delete = requests.delete(f"{server.server_address}authors/{author_id}/followers/{follower_id}", auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]))
    return delete.status_codes


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


# content is a json object
def SendContentToInbox(server, author_id, content):
    headers = {'Content-type': 'application/json'}

    req = requests.post(f"{server.server_address}authors/{author_id}/inbox",
        auth=HTTPBasicAuth(server.auth.split(":")[0], server.auth.split(":")[1]),
        data=content, headers=headers)

    return req.status_code < 299
