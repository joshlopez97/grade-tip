import re

from flask import current_app as app

from GradeTip.content.identifier import IDGenerator
from GradeTip.indexer.frequency import FrequencyStore


class DocumentSearch:
    def __init__(self, redis_values, listing_store):
        self.freq_store = FrequencyStore(redis_values)
        self.id_generator = IDGenerator()
        self.listing_store = listing_store

    @staticmethod
    def get_terms(query):
        """
        Get relevant search terms from query to search index for
        :param query: query to grab terms from
        :return: list of search terms
        """
        return re.findall(r'\w+', query)

    def get_post_id(self, upload_id):
        return upload_id[len(self.id_generator.prefixes.upload):]

    def search(self, query):
        app.logger.info("Fetching document results for \"{}\"".format(query))
        terms = self.get_terms(query)
        results = []
        listing_ids = set()
        for term in terms:
            tf_data = self.freq_store.get_tf(term)
            for upload_id, doc_data in tf_data.items():
                listing_id = self.get_post_id(upload_id)
                if listing_id not in listing_ids:
                    listing_ids.add(listing_id)
                    results += [self.listing_store.get_listing(listing_id)]
        return results
