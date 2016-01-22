"""
Created on 2015-07-05

@author: Valtyr Farshield
"""


class BbCommon:

    def __init__(self):
        pass

    @staticmethod
    def represents_float(s):
        # verifies if the string s is a float
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def represents_int(s):
        # verifies if the string s is a number
        try:
            int(s)
            return True
        except ValueError:
            return False
