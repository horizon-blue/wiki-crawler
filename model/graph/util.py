ROOT = "https://en.wikipedia.org"


def get_wiki_page(url):
    """
    A helper function to get the wiki page
    :param url: the link to wiki page
    """
    if isinstance(url, str) and url.startswith(ROOT):
        return url[len(ROOT):]
    else:
        return url
