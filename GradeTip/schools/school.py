import json
from flask import current_app as app


class SchoolStore:
    def __init__(self):
        self.college_data = {}
        with open('resources/course_catalog.json', 'r') as f:
            self.college_data = json.load(f)

    def get_college_data(self):
        """
        Returns all college data including college names, IDs, courses, and geographic info
        :return: dict containing college data
        """
        return self.college_data

    def get_school_id(self, school_name):
        """
        Returns unique ID of school with given name
        :param school_name: name of school
        :return: ID of school
        """
        return self.college_data.get(school_name).get('sid')

    def get_school_name(self, school_id):
        """
        Returns name of school with given ID
        :param school_id: ID of school
        :return: name of school
        """
        for school_name, school_data in self.college_data.items():
            if school_data.get("sid") == school_id:
                return school_name
        error_msg = "School with ID {} not found".format(school_id)
        app.logger.error(error_msg)
        raise ValueError(error_msg)
