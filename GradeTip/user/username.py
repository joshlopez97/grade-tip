import random

from GradeTip.redis.set import RedisSet


class UsernameGenerator:
    def __init__(self):
        self.displayNames = RedisSet("displayNames")
        self.nouns = []
        self.adjectives = []
        with open("resources/nouns.txt", "r") as f:
            self.nouns = [line.strip('\n') for line in f if line.strip('\n')]
        with open("resources/adjectives_names.txt", "r") as f:
            self.adjectives = [line.strip('\n') for line in f if line]

    def get_username(self):
        return random.choice(self.adjectives) + random.choice(self.nouns)

    def get_usernames_in_bulk(self, count=50):
        usernames = []
        while len(usernames) < count:
            username = self.get_username()
            if not self.displayNames.exists(username):
                usernames += [username]
        return usernames
