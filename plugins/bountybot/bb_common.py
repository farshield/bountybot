'''
Created on 2015-07-05

@author: Valtyr Farshield
'''

class BbCommon():
    @staticmethod
    def representsFloat(s):
        # verifies if the string s is a float
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def representsInt(s):
        # verifies if the string s is a number
        try:
            int(s)
            return True
        except ValueError:
            return False
