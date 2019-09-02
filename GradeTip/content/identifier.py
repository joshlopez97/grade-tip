import hashlib
from datetime import datetime
from random import random

from GradeTip.redis.set import RedisSet


class IDGenerator:
    def generate(self, prefix, email, set_name):
        """
        Generate unique ID, recursively regenerate on collision
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

    def _create_id_hash(self, prefix, email):
        """
        Creates ID using SHA1 hashing
        :param prefix: prefix to append to front of has
        :param email: email to hash
        :return: string containing new hash
        """
        return prefix + str(hashlib.sha1(email + datetime.now().microsecond + random.randint(10, 100)))
