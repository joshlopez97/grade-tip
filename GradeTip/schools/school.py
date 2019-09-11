import json


class Schools:
    def __init__(self):
        self.college_data = {}
        with open('resources/course_catalog.json', 'r') as f:
            self.college_data = json.load(f)

    def get_college_data(self):
        return self.college_data

    def get_school_id(self, school_name):
        return self.college_data.get(school_name).get('sid')

    def get_school_name(self, school_id):
        for school_name, school_data in self.college_data.items():
            if school_data.get("sid") == school_id:
                return school_name
        return ""
