# -*- coding: UTF-8 -*-
import json

from requests import post
import logging

logger = logging.getLogger(__name__)
production = False


class MoodleLib:
    def __init__(self):
        """
        Creates the connection with Moodle
        """
        moodle_user = "webserviceuser"
        url = "http://192.168.0.153/moodle"
        key = "4ee1b4ee0c79d92dd49c6ec3ffcf90ca"

        if production:
            moodle_user = "webserviceuser"
            url = "https://campus.isep.es"
            key = "4ee1b4ee0c79d92dd49c6ec3ffcf90ca"

        self.conn = url
        self.token = key

    def connect(self, function: str, params: dict) -> dict:
        """
        POST to Moodle the function and parameters specified

        :param function: str
        :param params: dict
        :return: dict
        """
        url = self.conn + "/webservice/rest/server.php"

        params.update({
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': function
        })
        response = post(url, params)
        source = response.json()
        if type(source) == dict and source.get('exception'):
            logger.info("Params: {}".format(json.dumps(params)))
            logger.info("Moodle response: {}".format(json.dumps(source)))
        elif response.status_code == 404:
            # raise UserError(_("Moodle error: failed connection"))
            print("Moodle error: failed connection")
        else:
            return source

    def moodle_function(self, function: str, params: dict) -> dict:
        return self.connect(function, params)

    def core_course_get_categories(self, key: str, value: str) -> dict:
        """
        params = {
            'criteria[0][key]': key,
            'criteria[0][value]': value
        }
        :param key: str
        :param value: str
        :return: dict
        """
        params = {
            'criteria[0][key]': key,
            'criteria[0][value]': value
        }
        function = "core_course_get_categories"
        return self.connect(function, params)

    def create_users(self, firstname: str, lastname: str, dni: str,
                     email: str, password: str) -> dict:
        """
        Function: core_user_create_users

        user_params = {
            'users[0][username]': username.lower(),
            'users[0][password]': password,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][idnumber]': id_number,
            'users[0][email]': email
        }
        :param password:
        :param firstname: str
        :param lastname: str
        :param dni: str
        :param email: str
        :return: dict
        """
        params = {
            'users[0][username]': email.lower(),
            'users[0][password]': password,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][idnumber]': dni,
            'users[0][email]': email
        }
        function = "core_user_create_users"
        return self.connect(function, params)

    def get_users_by_field(self, field: str, value: str) -> dict:
        """
        core_user_get_users_by_field, field: idnumber for student

        :param field: str
        :param value: str
        :return: dict
        """
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': value}
        return self.connect(function, params)

    def get_all_users(self) -> dict:
        """
        core_user_get_users, field: idnumber for student

        :return: dict
        """
        function = "core_user_get_users"
        params = {
            'criteria[0][key]': 'confirmed',
            'criteria[0][value]': 1
        }
        response = self.connect(function, params)
        return response['users']

    def get_user_by_field(self, field: str, value: str) -> dict:
        """
        core_user_get_users_by_field, field: idnumber for student

        :param field: str
        :param value: str
        :return: dict
        """
        function = "core_user_get_users_by_field"
        params = {'field': field, 'values[0]': value}
        users = self.connect(function, params)
        user = None
        if len(users) > 0:
            user = users[0]
        return user

    def get_course(self, name: str) -> dict:
        """
        core_course_search_courses

        :param name: str to search
        :return: dict of 1 course
        """
        function = "core_course_search_courses"
        params = {'criterianame': 'search', 'criteriavalue': name}
        courses = self.connect(function, params)
        course = None
        if courses is not None and courses["total"] > 0:
            course = courses["courses"][0]
        return course

    def get_course_by_field(self, field: str, value: str) -> dict:
        """
        core_course_get_courses_by_field

        :param field: str
        :param value: str
        :return: dict
        """
        function = "core_course_get_courses_by_field"
        params = {
            'field': field,
            'value': value
        }
        print(params)
        return self.connect(function, params)

    def get_group(self, course_id: int, group_id: str) -> dict:
        """
        core_group_get_course_groups

        :param course_id: int
        :param group_id: str
        :return: dict
        """
        function = "core_group_get_course_groups"
        params = {'courseid': course_id}
        groups = self.connect(function, params)
        group = None
        for row in groups:
            if row["name"] == group_id:
                group = row
        return group

    def core_group_create_groups(self, name: str, course_id: int) -> dict:
        """
        params = {
            'groups[0][description]': name,
            'groups[0][name]': name,
            'groups[0][courseid]': course_id,
        }

        :param name: str
        :param course_id: int
        :return: dict
        """
        params = {
            'groups[0][description]': name,
            'groups[0][name]': name,
            'groups[0][courseid]': course_id,
        }
        function = "core_group_create_groups"
        return self.connect(function, params)

    def get_category_by_field(self, key: str, value: str) -> dict:
        """
        core_course_get_categories

        :param key: str
        :param value: str
        :return: dict
        """
        function = "core_course_get_categories"
        params = {
            'criteria[0][key]': key,
            'criteria[0][value]': value
        }
        return self.connect(function, params)

    def delete_users(self, user_id: int) -> dict:
        """
        Function: core_user_delete_users

        params = {'userids[0]': user_id}
        :param user_id: int
        :return: dict
        """
        function = "core_user_delete_users"
        params = {'userids[0]': user_id}
        return self.connect(function, params)

    def enrol_user(self, course_id: str, user_id: int) -> dict:
        """
        enrol_manual_enrol_users

        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        :param course_id: str
        :param user_id: int
        :return: dict
        """
        function = "enrol_manual_enrol_users"
        params = {
            'enrolments[0][courseid]': course_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][roleid]': 5
        }
        return self.connect(function, params)

    def add_group_members(self, group_id: int, user_id: int) -> dict:
        """
        core_group_add_group_members

        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }

        :param group_id: int
        :param user_id: int
        :return: dict
        """
        function = "core_group_add_group_members"
        params = {
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }
        return self.connect(function, params)
