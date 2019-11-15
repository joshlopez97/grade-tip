import hashlib
from datetime import datetime
import random

from GradeTip.redis.set import RedisSet


class NameProvider:
    """
    Generates unique IDs and provides names/keys/prefixes for all data stored in Redis
    """

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
        set_name = self.set_names.post(school_id)
        return self.generate(self.prefixes.post, email, set_name)

    def generate_listing_id(self, email, school_id):
        """
        Generate unique ID for a listing
        :param school_id: ID of school where listing was made
        :param email: email of user
        :return: string containing ID
        """
        set_name = self.set_names.listing(school_id)
        return self.generate(self.prefixes.listing, email, set_name)

    def generate_reply_id(self, email, content_id):
        """
        Generates unique ID for a reply
        :param email: email of user
        :param content_id: ID of content being replied to
        :return: string containing ID
        """
        set_name = self.set_names.reply(content_id)
        return self.generate(self.prefixes.reply, email, set_name)

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
        :param prefix: prefix to append to front of hash
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
        self.reply = "re-"

        # search-related data
        self.df = "df-"
        self.tf = "tf-"

        # IP Address cache
        self.ip = "ip-"


class SetNames:
    def __init__(self):
        self.request = "requests"
        self.cached_ips = "cached_ips"
        self._post = "posts-"
        self._listing = "listings-"
        self._reply = "replies-"

    def listing(self, school_id):
        return "{}{}".format(self._listing, school_id)

    def post(self, school_id):
        return "{}{}".format(self._post, school_id)

    def reply(self, content_id):
        return "{}{}".format(self._reply, content_id)


class ValueNames:
    def __init__(self):
        self.doc_count = "doc_count"
