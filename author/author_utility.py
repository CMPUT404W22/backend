import re

from author.models import Author
from author.serializer import AuthorSerializer
from server_api.external import GetAuthor
from server_api.models import Server


def get_author(url):
    author_id = get_author_id(url)
    origin, server = get_node(url)

    if origin == "local":
        return AuthorSerializer(Author.objects.get(id=author_id), many=False).data
    else:
        return GetAuthor(server, author_id)


def get_author_id(url):
    result = re.findall("(?<=authors/).*?(?=/)", url)
    if len(result) == 0:
        result = re.findall("(?<=authors/).*", url)
        return result[0]
    else:
        return result[0]


def get_node(url):
    if "127.0.0.1" in url or "cmput404-w22-project-backend.herokuapp.com" in url:
        return "local", None
    else:
        server = Server.objects.get(server_address__icontains=url.split("author")[0][7:-7])
        return "foreign", server
