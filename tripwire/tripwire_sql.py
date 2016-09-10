"""
Created on 2016-08-27

@author: Valtyr Farshield
"""

import re
import datetime
import MySQLdb


class TripwireSql:
    """
    Tripwire SQL comments for @bountybot
    """
    specific_message = "This is a bounty system!"
    generic_message = "This is a potential generic bounty system. Please verify if the requirements are met."
    message_suffix = '<span style="font-size:9px;"><em><span style="color:#D3D3D3;">' \
                     'Please do not remove or modify this comment.</span></em></span>'

    def __init__(self, user, passwd, mask, trip_char_id, host='127.0.0.1', port=3306, db='tripwire'):
        self.mask = mask
        self.trip_char_id = trip_char_id
        self.db_con = MySQLdb.connect(
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            db=db,
            charset='utf8'
        )
        self.cursor = self.db_con.cursor()

    @staticmethod
    def _time_now():
        return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _get_comments(self, system_id):
        query = "SELECT id, comment FROM comments WHERE systemID=%s AND createdBy=%s AND maskID=%s"
        self.cursor.execute(query, (system_id, self.trip_char_id, self.mask))
        return self.cursor.fetchall()

    def _add_comment(self, system_id, comment_text):
        query = """\
            INSERT INTO comments (systemID, comment, created, createdBy, modifiedBy, maskID)
            VALUES (%s, %s, %s, %s, %s, %s)\
            """
        self.cursor.execute(
            query, (system_id, comment_text, self._time_now(), self.trip_char_id, self.trip_char_id, self.mask)
        )

    def _edit_comment(self, comment_id, comment_text):
        query = "UPDATE comments SET comment=%s, modified=%s, modifiedBy=%s WHERE id=%s"
        self.cursor.execute(query, (comment_text, self._time_now(), self.trip_char_id, comment_id))

    def _delete_comment(self, comment_id):
        query = "DELETE FROM comments WHERE id=%s"
        self.cursor.execute(query, (comment_id, ))

    def add_or_update_specific(self, system_id, comment_text):
        """
        Update or add the comment associated with a specific bounty wormhole
        :param system_id: Wormhole system ID
        :param comment_text: New message
        :return: None
        """
        comment = '<span style="color: rgb(178, 34, 34); font-family: Arial; font-size: 21px; line-height: normal; ' \
            'white-space: pre-wrap; background-color: rgb(0, 0, 0);">{} {}</span><br /><br />{}'.format(
                self.specific_message,
                comment_text,
                self.message_suffix
            )
        result = self._get_comments(system_id)
        if len(result) > 0:
            found = False
            for comment_id, comment_text in result:
                if self.specific_message in comment_text:
                    self._edit_comment(comment_id, comment)
                    found = True
            if not found:
                self._add_comment(system_id, comment)
        else:
            self._add_comment(system_id, comment)

    def delete_specific(self, system_id):
        """
        Delete the comment associated with a specific bounty wormhole
        :param system_id: Wormhole system ID
        :return: None
        """
        result = self._get_comments(system_id)
        for comment_id, comment_text in result:
            if self.specific_message in comment_text:
                self._delete_comment(comment_id)

    def _construct_generic_comment(self, generic_orders):
        comment = '<span style="color:#FFD700;">{}</span><br /><br />'.format(self.generic_message)
        for key in generic_orders:
            comment += '<span style="font-size:9px;">[<span style="color:#00FF00;">#{}:</span> {}]</span>'.format(
                key,
                generic_orders[key]
            )
            comment += '<br />'
        comment += '<br />' + self.message_suffix
        return comment

    def add_generic(self, generic_id, description, system_ids):
        for sys_id in system_ids:
            comment_id_found = None
            generic_orders = {
                str(generic_id): description,
            }

            result = self._get_comments(sys_id)
            for comment_id, comment_text in result:
                if self.generic_message in comment_text:
                    comment_id_found = comment_id
                    for idx, desc in re.findall(
                            '\[<span style="color:#00FF00;">#([0-9]+):</span> (.*?)\]',
                            comment_text
                    ):
                        generic_orders[idx] = desc
                    break

            # add/update comment
            comment = self._construct_generic_comment(generic_orders)
            if comment_id_found:
                self._edit_comment(comment_id_found, comment)
            else:
                self._add_comment(sys_id, comment)

    def delete_generic(self, generic_id, system_ids):
        for sys_id in system_ids:
            comment_id_found = None
            generic_orders = {}

            result = self._get_comments(sys_id)
            for comment_id, comment_text in result:
                if self.generic_message in comment_text:
                    comment_id_found = comment_id
                    for idx, desc in re.findall(
                            '\[<span style="color:#00FF00;">#([0-9]+):</span> (.*?)\]',
                            comment_text
                    ):
                        generic_orders[idx] = desc
                    break

            # remove/update comment
            if comment_id_found:
                if len(generic_orders) > 1:
                    if str(generic_id) in generic_orders.keys():
                        del generic_orders[str(generic_id)]
                    comment = self._construct_generic_comment(generic_orders)
                    self._edit_comment(comment_id_found, comment)
                else:
                    if str(generic_id) in generic_orders.keys():
                        self._delete_comment(comment_id_found)

    def close_db(self):
        self.db_con.commit()
        self.db_con.close()
