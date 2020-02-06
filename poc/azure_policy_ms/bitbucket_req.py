from os import environ
import re
import requests

user = environ.get("SOCIALCODING_USER")
pw = environ.get("SOCIALCODING_PW")

def get_from_bitbucket(url):
    """Gets the json resource at the given url from bitbucket
    
    Parameters:
    url (String): bitbucket/socialcoding url of the policy resource

    Returns:
    dict: json object of the element at the given url
    """

    # replace browse with raw in request url
    url = url.replace("/browse/", "/raw/", 1)

    r = requests.get(url, auth=(user, pw))
    
    return r.json()
