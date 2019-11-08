import hashlib
from datetime import datetime
import random

from GradeTip.redis.set import RedisSet


class IDGenerator:
    def __init__(self):
        self.prefixes = Prefixes()
        self.set_names = SetNames()
        self.value_names = ValueNames()

    def generate_request_id(self, email):
        """
        Generate unique ID for a request
        :param email: email of user
        :return: string containing ID
        """
        return self.generate(self.prefixes.request, email, self.set_names.request)

    def generate_post_id(self, email, school_id):
        """
        Generate unique ID for a post
        :param school_id: ID of school where post was made
        :param email: email of user
        :return: string containing ID
        """
        set_name = "{}/{}".format(self.set_names.post, school_id)
        return self.generate(self.prefixes.post, email, set_name)

    def generate_listing_id(self, email, school_id):
        """
        Generate unique ID for a listing
        :param school_id: ID of school where listing was made
        :param email: email of user
        :return: string containing ID
        """
        set_name = "{}/{}".format(self.set_names.listing, school_id)
        return self.generate(self.prefixes.listing, email, set_name)

    def generate(self, prefix, email, set_name):
        """
        Generate unique ID, recursively regenerate on collision. Store unique ID
        in redis set named set_name.
        :param email: email of user (used for creating hash)
        :param prefix: prefix to give to ID
        :param set_name: name of Redis set to look for ID collisions
        :return: string containing ID
        """
        identifier = self._create_id_hash(prefix, email)

        # ensure id is unique (no collisions)
        if RedisSet(set_name).add([identifier]) == 0:
            return self.generate(prefix, email, set_name)
        return identifier

    def generate_upload_id(self, post_id):
        return "{}{}".format(self.prefixes.upload, post_id)

    @staticmethod
    def _create_id_hash(prefix, email):
        """
        Creates ID using SHA1 hashing
        :param prefix: prefix to append to front of has
        :param email: email to hash
        :return: string containing new hash
        """
        encoded_str = (email + str(datetime.now().microsecond) + str(random.randint(10, 100))).encode('utf-8')
        return prefix + hashlib.sha1(encoded_str).hexdigest()


class Prefixes:
    def __init__(self):
        # user-created content
        self.request = "r-"
        self.listing = "l-"
        self.upload = "u-"
        self.post = "p-"

        # search-related data
        self.df = "df-"
        self.tf = "tf-"


class SetNames:
    def __init__(self):
        self.request = "requests"
        self.post = "posts"
        self.listing = "listings"


class ValueNames:
    def __init__(self):
        self.doc_count = "doc_count"
