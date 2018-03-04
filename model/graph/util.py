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


def get_filter(item):
    """
    A helper function to return the filter that contains the name
    and wiki_page in item, if exist
    :param item: the dictionary or scrapy item object
    :return: the dictionary represent filter
    """
    query_filter = {}
    if "name" in item:
        query_filter["name"] = item.get("name")
    if "wiki_page" in item:
        query_filter["wiki_page"] = get_wiki_page(item.get("wiki_page"))
    return query_filter
