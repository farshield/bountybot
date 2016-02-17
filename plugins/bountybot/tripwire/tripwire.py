"""
Created on 2016-02-17

@author: Valtyr Farshield
"""

import requests
import urlparse


class Tripwire:
    """
    Tripwire handler
    """

    def __init__(self, username, password, url="https://tripwire.eve-apps.com"):
        self.username = username
        self.password = password
        self.url = url
        self.session_requests = self.login()

    def login(self):
        result = None
        login_url = urlparse.urljoin(self.url, "login.php")
        session_requests = requests.session()

        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            result = session_requests.post(
                login_url,
                data=payload,
                headers=dict(referer=login_url)
            )
        except requests.exceptions.ConnectionError as e:
            print e
        except requests.exceptions.RequestException as e:
            print e

        if result is not None:
            if result.status_code == 200:
                return session_requests

        return None

    def add_comment(self, system_id, comment):
        response = None

        if self.session_requests is not None:
            comment_url = urlparse.urljoin(self.url, "comments.php")
            payload = {
                "mode": "save",
                "systemID": system_id,
                "comment": comment
            }

            result = self.session_requests.post(
                comment_url,
                data=payload,
                headers=dict(referer=comment_url)
            )

            if result.status_code == 200:
                response = result.json()

        return response

    def get_comments(self, system_id):
        response = []

        if self.session_requests is not None:
            refresh_url = urlparse.urljoin(self.url, "refresh.php")
            payload = {
                "mode": "refresh",
                "systemID": system_id
            }

            result = self.session_requests.get(
                refresh_url,
                params=payload
            )

            if result.status_code == 200:
                json_response = result.json()
                if "comments" in json_response.keys():
                    response = json_response["comments"]

        return response

    def get_comments_by_name(self, system_id, name):
        response = []
        all_comments = self.get_comments(system_id)

        for comment in all_comments:
            if comment["createdBy"] == name:
                response.append(comment)

        return response

    def edit_comment(self, system_id, comment_id, comment):
        response = None

        if self.session_requests is not None:
            comment_url = urlparse.urljoin(self.url, "comments.php")
            payload = {
                "mode": "save",
                "commentID": comment_id,
                "systemID": system_id,
                "comment": comment
            }

            result = self.session_requests.post(
                comment_url,
                data=payload,
                headers=dict(referer=comment_url)
            )

            if result.status_code == 200:
                response = result.json()

        return response

    def delete_comment(self, comment_id):
        response = None

        if self.session_requests is not None:
            comment_url = urlparse.urljoin(self.url, "comments.php")
            payload = {
                "mode": "delete",
                "commentID": comment_id,
            }

            result = self.session_requests.post(
                comment_url,
                data=payload,
                headers=dict(referer=comment_url)
            )

            if result.status_code == 200:
                response = result.json()

        return response

    def delete_comments_by_name(self, system_id, name):
        response = []

        comments_by_name = self.get_comments_by_name(system_id, name)
        for comment in comments_by_name:
            response.append(self.delete_comment(comment["id"]))

        return response


def main():
    trip = Tripwire("username", "password")

if __name__ == "__main__":
    main()
