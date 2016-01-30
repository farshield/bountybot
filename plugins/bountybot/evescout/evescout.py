"""
Created on 2015-05-11

@author: Valtyr Farshield
"""

import urllib2
import json
import gzip
import re
from StringIO import StringIO


class EveScout:
    """
    Eve Scout Thera Connections
    """

    def __init__(self):
        pass

    @staticmethod
    def thera_connections():
        wh_systems = []
        headers = {
            "User-Agent": "Wingspan Bounty Bot",
            "Accept-encoding": "gzip"
        }
        url = "https://www.eve-scout.com/api/wormholes"

        try:
            request = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
            print "[Error]", e.reason
        else:
            if response.info().get("Content-Encoding") == "gzip":
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = response.read()

            # try to parse JSON received from server
            try:
                parsed_json = json.loads(data)
            except ValueError as e:
                print "[Error]", e
            else:
                if len(parsed_json) > 0:
                    for item in parsed_json:
                        system_name = item['destinationSolarSystem']['name']
                        match_obj = re.search("J[0-9-]{6}", system_name)
                        if match_obj:
                            wh_systems.append(system_name)

        return wh_systems


def main():
    print EveScout.thera_connections()

if __name__ == "__main__":
    main()
