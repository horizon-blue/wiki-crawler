from urllib.parse import unquote


def decode(string):
    """
    Helper function to decode url-string and remove quote
    :param string: the string to decode
    :return: the decoded string
    """
    return unquote(string.replace("%22", ""))


def parse_query(query_string):
    """
    parse query to a list of key-value pair. Does not do type-checking
    and may throws exception
    :param query_string: the string represents the query
    :return: a list of dictionary represents the query
    """
    result = []
    if query_string is None or query_string == "":
        return result

    for query in query_string.split('|'):
        query_dict = {}
        for attr in query.split('&'):
            pair = attr.split('=')
            if len(pair) != 2:
                raise ValueError("incorrect number of arguments")
            query_dict[decode(pair[0])] = decode(pair[1])
        result.append(query_dict)
    return result
