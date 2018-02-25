from abc import ABC, abstractmethod


class Node(ABC):
    name = None
    url = None

    def __eq__(self, other):
        """
        check equality of two nodes. two nodes are considered equal if
        and only their url are equal
        In addition, a string is equal to the node if it is the same as the node's url
        :param other: the other node to compare
        :return: true if the two nodes have the same url, false otherwise
        """
        if isinstance(other, str):
            return self.url == other
        return isinstance(other, self.__class__) and self.url == other.url

    def __hash__(self):
        """
        node with same url should have same hash
        :return: hash that uniquely identify the node
        """
        return hash(self.url)
