from GradeTip import college_data


def get_school_id(school_name):
    return college_data.get(school_name).get('sid')


def get_school_name(school_id):
    for school_name, school_data in college_data.items():
        if school_data.get("sid") == school_id:
            return school_name
    return None
