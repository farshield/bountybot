"""
Created on 2016-08-27

@author: Valtyr Farshield
"""

import datetime
import MySQLdb


class TripwireSql:
    """
    Tripwire SQL comments for @bountybot
    """
    specific_message = "This is a bounty system!"
    message_suffix = '<br /><br /><span style="font-size:9px;"><em><span style="color:#D3D3D3;">' \
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
            'white-space: pre-wrap; background-color: rgb(0, 0, 0);">{} {}</span>{}'.format(
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

    def close_db(self):
        self.db_con.commit()
        self.db_con.close()
