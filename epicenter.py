"""
Created on 2015-05-30

@author: Valtyr Farshield
"""

import re
import sqlite3 as lite
from bb_common import BbCommon


class Epistatic:
    def __init__(self, static_code, wh_class, stabletime, maxjump, maxmass, info):
        self.static_code = static_code
        self.wh_class = wh_class
        self.stabletime = stabletime
        self.maxjump = maxjump
        self.maxmass = maxmass
        self.info = info
        
    def __str__(self):
        message = "*{}* - Leads to: {}, Stable Time: {} hrs, Mass/Jump: {} kT, Max Mass: {} kT".format(
                   self.static_code, self.wh_class, self.stabletime, self.maxjump, self.maxmass)
        
        if self.info is not None:
            message += ", Info: {}".format(self.info)
        
        return message


class Epiwh:
    planet_types = ["Temperate", "Ice", "Gas", "Oceanic", "Lava", "Barren", "Storm", "Plasma", "Shattered"]
    effect_types = ["Black Hole", "Cataclysmic Variable", "Magnetar", "No effect", "Pulsar", "Red Giant",
                    "Wolf-Rayet Star"]
    
    #             [T, I, G, O, L, B, S, P, Sh]
    perfect_pi = [[1, 1, 1, 0, 1, 1, 0, 0, 0],
                  [1, 1, 1, 0, 1, 0, 0, 1, 0],
                  [1, 0, 1, 1, 1, 1, 0, 0, 0],
                  [1, 0, 1, 1, 1, 0, 0, 1, 0]]
    
    def __init__(self, sysId, name, wh_class, effect, radius, statics, targets, moons, planets, info):
        self.sysId = sysId         # internal Eve Id of system [private]
        self.name = name           # name of the wormhole (ex. J123450)
        self.wh_class = wh_class   # Wormhole class 1-6, 13-18
        self.effect = effect       # Wormhole effect (ex. Magnetar)
        self.radius = radius       # Distance from sun to furthest planet
        self.statics = statics     # List of statics (ex. B274 D385 Q003)
        self.targets = targets     # List of targets (ex. HS C2 NS)
        self.moons = moons         # Number of moons
        self.planets = planets     # List of planets in format [T, I, G, O, L, B, St, P, Sh]
        self.info = info           # Additional information (optional)
    
    # pretty print
    def __str__(self):
        output_str = "*{}* [C{}] {}, Radius: {} AU, Moons: {}, Statics: {}".format(
            self.name,
            self.wh_class,
            self.effect,
            self.radius,
            self.moons,
            self.statics
        )
        
        target_list = self.__translate_statics()
        if target_list:
            output_str += " ("
            output_str += " ".join(target_list)
            output_str += ")"
        
        if self.info is not None:
            output_str += ", Other info: {}".format(self.info)
        
        return output_str
    
    # convert statics (e.g. B274 Y683 -> HS C4)
    def __translate_statics(self):
        target_list = []
        for target in self.targets:
            if target == Epicenter.HS_CODE:
                target_list.append("HS")
            elif target == Epicenter.LS_CODE:
                target_list.append("LS")
            elif target == Epicenter.NS_CODE:
                target_list.append("NS")
            else:
                target_list.append("C" + str(target))
        return target_list
    
    # returns a human readable text info on the planets of the current system
    def planet_info(self):
        output_info = ">Planets: "
        planet_list = []
        
        for idx, planet_type in enumerate(Epiwh.planet_types):
            if self.planets[idx] != 0:
                planet_list += ["{}: {}".format(planet_type, self.planets[idx])]
        
        output_info += ", ".join(planet_list)
        
        # Check if system has perfect P.I.
        if self.__has_perfect_pi():
            output_info += " `Perfect P.I.`"
        
        return output_info
    
    # returns a human readable text info on the planets of the current system
    def compact_planet_info(self):
        output_info = "Planets: "
        planet_list = []
        
        for idx, planet_type in enumerate(Epiwh.planet_types):
            if self.planets[idx] != 0:
                planet_list += ["{}-{}".format(planet_type[0], self.planets[idx])]
        
        output_info += ", ".join(planet_list)
        
        # Check if system has perfect P.I.
        if self.__has_perfect_pi():
            output_info += " `Perfect P.I.`"
        
        return output_info
    
    # return True if current wormhole meets the requirements of planet_list
    def __planet_match(self, planets):
        for idx, planet in enumerate(planets):
            if planet > self.planets[idx]:
                return False
        
        return True
    
    # Checks if the current wormhole has perfect P.I.
    def __has_perfect_pi(self):
        for planets in Epiwh.perfect_pi:
            if self.__planet_match(planets):
                return True
        
        return False
    
    # check if this particular wormhole meets the criteria given as parameters
    def matchCrit(self, class_list, effect_list, static_params, radius_list, moon_list, planet_list, planetNr_list):
        
        # Only proceed if wormhole classes match
        if self.wh_class in class_list:
            
            # process effect
            if effect_list:
                if self.effect not in effect_list:
                    return False
            
            # process statics
            if static_params:
                static_list = static_params[0]
                exclude = static_params[1]
                
                if static_list:
                    
                    if exclude:
                        # exclude keyword detected
                        for static in static_list[0]:
                            if static in self.targets:
                                return False
                    else:
                        # do not exclude
                        found = False
                        for statics in static_list:
                            if set(statics) <= set(self.targets):
                                found = True
                        
                        if not found:
                            return False
            
            # process radius
            if radius_list:
                min_rad = radius_list[0]
                max_rad = radius_list[1]
                if self.radius > max_rad or self.radius < min_rad:
                    return False
            
            # process moons
            if moon_list:
                min_moons = moon_list[0]
                max_moons = moon_list[1]
                
                if self.moons > max_moons or self.moons < min_moons:
                    return False
            
            # process number of planets
            if planetNr_list:
                planets_nr = sum(self.planets)
                min_planets = planetNr_list[0]
                max_planets = planetNr_list[1]
                
                if planets_nr > max_planets or planets_nr < min_planets:
                    return False
                
            # process planets
            if planet_list:
                found = False
                
                for planets in planet_list:
                    if self.__planet_match(planets):
                        found = True
                        
                if not found:
                    return False
            
            # everything checked out, return True
            return True
            
        else:
            # Wormhole class does not match
            return False


class Epicenter:
    Delimiter = ";"
    HS_CODE = 100
    LS_CODE = 200
    NS_CODE = 300
    
    # constructor
    def __init__(self, db_name, table_wh, table_statics):
        
        self.db_name = db_name               # epicenter database name
        self.table_wh = table_wh             # table name where info on wormholes is stored
        self.table_statics = table_statics   # table name where info on static codes is stored
        self.__epistatics = []               # ram mirror of statics table
        self.__epiwhlist = []                # ram mirror of wormhole table
        
        # database connection
        self.db_con = lite.connect(self.db_name)
        self.cursor = self.db_con.cursor()
        
        # -----------------------------------------------------------------------------
        # load statics data
        statement = "SELECT * FROM {}".format(self.table_statics)
            
        result = self.cursor.execute(statement)
        for row in result:
            epix = Epistatic(row[0], row[1], int(row[2]), int(row[3]), int(row[4]), row[5])
            self.__epistatics.append(epix)
        
        # -----------------------------------------------------------------------------
        # load wormhole data
        statement = """SELECT SysId, Name, Class, Effect, Radius, Statics, Moons,
            Temperate, Ice, Gas, Oceanic, Lava, Barren, Storm, Plasma, Shattered, Info FROM {}""".format(self.table_wh)
            
        result = self.cursor.execute(statement)
        for row in result:
            planets = [row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]]
            epiwh = Epiwh(row[0], row[1], row[2], row[3], row[4], row[5], [], row[6], planets, row[16])
            
            # compute static targets list
            if epiwh.statics.lower() != "unknown":
                for static_code in epiwh.statics.split():
                    target = self.convertStatic(static_code)
                    
                    if target == "HS":
                        epiwh.targets.append(Epicenter.HS_CODE)
                    elif target == "LS":
                        epiwh.targets.append(Epicenter.LS_CODE)
                    elif target == "NS":
                        epiwh.targets.append(Epicenter.NS_CODE)
                    elif target[0] == "C":
                        epiwh.targets.append(int(target[1:]))
                    else:
                        # unknown target system - ignore
                        pass
            
            self.__epiwhlist.append(epiwh)
            # print epiwh
        
        # database connection not needed anymore
        self.__closeDb()

    # Get the internal system Id of the wormhole
    def getSysId(self, name):
        try:
            sysId = next(epiwh for epiwh in self.__epiwhlist if epiwh.name == name).sysId
        except StopIteration:
            sysId = 0
        
        return sysId
    
    # Get the class of the wormhole
    def getClass(self, name):
        try:
            wh_class = next(epiwh for epiwh in self.__epiwhlist if epiwh.name == name).wh_class
        except StopIteration:
            wh_class = 0
        
        return wh_class
    
    # Get information about a static code
    def getStatic(self, static_code):
        static_code = static_code.upper()
        for epistatic in self.__epistatics:
            if static_code == epistatic.static_code:
                return str(epistatic)
            
        return "Code '{}' not found in database".format(static_code)

    # Get mass of a static code
    def static_mass(self, static_code):
        static_code = static_code.upper()
        for epistatic in self.__epistatics:
            if static_code == epistatic.static_code:
                return [float(epistatic.maxmass), float(epistatic.maxjump)]

        return [0, 0]
    
    # Find out the target system of the static code
    def convertStatic(self, static_code):
        try:
            target_sys = next(
                epistatic for epistatic in self.__epistatics if epistatic.static_code == static_code
            ).wh_class
        except StopIteration:
            target_sys = "Unk"
        
        return target_sys

    # Retrieve overall information on a wormhole
    def info(self, name):
        try:
            epiwh = next(epiwh for epiwh in self.__epiwhlist if epiwh.name == name)
        except StopIteration:
            epiwh = None
            
        if epiwh is not None:
            output_info = str(epiwh)
        else:
            output_info = "Unknown wormhole"
            
        return output_info
    
    # Retrieve planet information on a wormhole
    def planets(self, name, display_compact=False):
        try:
            epiwh = next(epiwh for epiwh in self.__epiwhlist if epiwh.name == name)
        except StopIteration:
            epiwh = None
            
        if epiwh is not None:
            if display_compact:
                output_info = epiwh.compact_planet_info()
            else:
                output_info = epiwh.planet_info()
        else:
            output_info = "Unknown wormhole"
            
        return output_info
    
    # Close connection to database
    def __closeDb(self):
        # closing database
        self.db_con.close()

    # -----------------------------------------------------------------------------
    # Generic Stuff
    # -----------------------------------------------------------------------------

    # Compute integer range (e.g. 4-10)
    def __computeIntRange(self, text):
        min_nr = 0
        max_nr = 0
        
        matchObj = re.search("([0-9]+)-([0-9]+)", text, re.I)
        if matchObj:
            min_str = matchObj.group(1)
            max_str = matchObj.group(2)

            if BbCommon.represents_int(min_str) and BbCommon.represents_int(max_str):
                min_nr = int(min_str)
                max_nr = int(max_str)
        
        # min should be smaller than max
        if matchObj and min_nr <= max_nr:
            return [min_nr, max_nr]
        else:
            return []
        
    # Compute floating range (e.g 14.3-28.1)
    def __computeFloatRange(self, text):
        min_nr = 0
        max_nr = 0
        
        matchObj = re.search("([.0-9]+)-([.0-9]+)", text, re.I)
        if matchObj:
            min_str = matchObj.group(1)
            max_str = matchObj.group(2)

            if BbCommon.represents_float(min_str) and BbCommon.represents_float(max_str):
                min_nr = float(min_str)
                max_nr = float(max_str)
        
        # maximum radius should be greater than zero and min should be smaller than max
        if matchObj and max_nr != 0 and min_nr <= max_nr:
            return [min_nr, max_nr]
        else:
            return []

    # -----------------------------------------------------------------------------
    # Compute effects
    def __computeEffects(self, text):
        effect_local = ["black hole", "cataclysmic", "magnetar", "no effect", "pulsar", "red giant", "wolf-rayet"]
        
        effect_list = []
        exclude = False
        
        if "exclude" in text:
            exclude = True
            effect_list = list(Epiwh.effect_types)
        
        for idx, effect in enumerate(effect_local):
            if effect in text:
                if exclude:
                    effect_list.remove(Epiwh.effect_types[idx])
                else:
                    effect_list.append(Epiwh.effect_types[idx])
        
        return effect_list

    # Compute statics
    def __computeStatics(self, text):
        static_list = []
        exclude = True if "exclude" in text else False
        
        for group in text.split(" or "):
            sub_list = []
            
            if any(substr in group for substr in ["hs", "high-sec"]):
                sub_list.append(Epicenter.HS_CODE)
            
            if any(substr in group for substr in ["ls", "low-sec"]):
                sub_list.append(Epicenter.LS_CODE)
                
            if any(substr in group for substr in ["ns", "null-sec", "nul-sec"]):
                sub_list.append(Epicenter.NS_CODE)
            
            class_text = re.findall("C([0-9]{1,2})", group, re.I)
            for wh_class in class_text:
                sub_list.append(int(wh_class))
            
            if sub_list:
                static_list.append(sub_list)
        
        return [static_list, exclude]

    # Compute radius
    def __computeRadius(self, text):
        return self.__computeFloatRange(text)

    # Compute number of moons
    def __computeNrMoons(self, text):
        return self.__computeIntRange(text)

    # Number of planets of a given type
    def __getPlanet(self, text, pattern_list):
        for pattern in pattern_list:
            regex_pattern = pattern + "([0-9]+)"
            matchObj = re.search(regex_pattern, text, re.I)
            if matchObj:
                nr_planets = int(matchObj.group(1))
                return nr_planets
        
        return 0

    # Compute planets
    def __computePlanets(self, text):
        planet_list = []
        
        # Check if perfect P.I. is wanted
        if "perfect" in text:
            planet_list = Epiwh.perfect_pi
        else:
            for group in text.split(" or "):
                planets = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                
                planets[0] = self.__getPlanet(group, ["temperate-", "t-"])
                planets[1] = self.__getPlanet(group, ["ice-", "i-"])
                planets[2] = self.__getPlanet(group, ["gas-", "g-"])
                planets[3] = self.__getPlanet(group, ["oceanic-", "o-"])
                planets[4] = self.__getPlanet(group, ["lava-", "l-"])
                planets[5] = self.__getPlanet(group, ["barren-", "b-"])
                planets[6] = self.__getPlanet(group, ["storm-", "s-"])
                planets[7] = self.__getPlanet(group, ["plasma-", "p-"])
                planets[8] = self.__getPlanet(group, ["shattered-", "sh-"])
                
                if planets != [0, 0, 0, 0, 0, 0, 0, 0, 0]:
                    planet_list.append(planets)
        
        return planet_list
    
    # Compute number of planets
    def __computeNrPlanets(self, text):
        return self.__computeIntRange(text)
    
    # -----------------------------------------------------------------------------
    # Compute jcodes from a generic order
    def computeGeneric(self, text):
        jcodes = []       # the output
        
        class_list = []     # list of ordered classes (mandatory)
        effect_list = []    # list of ordered effects (optional)
        static_params = []  # list of ordered statics[can be list of lists] + exclude flag (optional)
        radius_list = []    # min and max radius (optional)
        moon_list = []      # min and max moons (optional)
        planet_list = []    # list of planets (optional)
        planetNr_list = []  # min and max planets (optional)
        
        text = text.lower()  # work with lower case to simplify process
        groups = text.split(Epicenter.Delimiter)  # split order into groups
        
        # class group (should always be the first one in group)
        if len(groups) > 0:
            if "sansha" in groups[0]:
                return ["Matches: 2; Processed: Sansha Override!", ['J005299', 'J010556']]

            if "all" in groups[0]:
                class_list = [1, 2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18]
            else:
                if "tripnull" in groups[0]:
                    class_list += [13]
                
                if "drifter" in groups[0]:
                    class_list += [14, 15, 16, 17, 18]
                    
                class_text = re.findall("C([0-9]{1,2})", groups[0], re.I)
                for wh_class in class_text:
                    class_list.append(int(wh_class))
            
            # determine if a shattered wormhole is wanted
            if "non-shattered" in groups[0]:
                moon_list = [1, 1000]
            elif "shattered" in groups[0]:
                moon_list = [0, 0]
        
        # only proceed if we determind which class (classes) bountybot should search for
        if len(class_list) > 0:
            
            for group in groups[1:]:
                
                # effect group
                if any(substr in group for substr in ["effect", "effects"]):
                    if not effect_list:
                        effect_list = self.__computeEffects(group)
                
                # statics group
                elif any(substr in group for substr in ["static", "statics"]):
                    if not static_params:
                        static_params = self.__computeStatics(group)
                
                # radius group (min, max) - default 'min'
                elif any(substr in group for substr in ["radius", "size"]):
                    if not radius_list:
                        radius_list = self.__computeRadius(group)
                
                # planets group
                elif any(substr in group for substr in ["planet", "planets", "p.i."]):
                    if not planet_list:
                        planet_list = self.__computePlanets(group)
                    
                    if not planetNr_list:
                        planetNr_list = self.__computeNrPlanets(group)
                
                # nr. of moons group (min, max, exact) - default 'exact'
                elif any(substr in group for substr in ["moon", "moons"]):
                    if not moon_list:
                        moon_list = self.__computeNrMoons(group)
                
                # nothing found, must be a comment?
                else:
                    pass
        
        # try to match wormholes respecting the given criteria
        for epiwh in self.__epiwhlist:
            if epiwh.matchCrit(class_list, effect_list, static_params, radius_list, moon_list, planet_list,
                               planetNr_list):
                jcodes.append(epiwh.name)
        
        # determine which user input has been given consideration
        processed = []
        if not class_list:
            processed.append("none")
        else:
            processed.append("class")
            if effect_list:
                processed.append("effects")
            if static_params:
                if static_params[0]:
                    processed.append("statics")
            if radius_list:
                processed.append("radius")
            if moon_list:
                processed.append("moons")
            if planet_list:
                processed.append("planets")
            if planetNr_list:
                processed.append("planet numbers")
        
        # construct result message
        matches = len(jcodes)
        processed = ", ".join(processed)
        processed += "."
        result_info = "Matches: {}; Processed: {}".format(matches, processed)
        
        # debugging
        # print "Class:", class_list
        # print "Effects:", effect_list
        # print "Statics:", static_params
        # print "Radius:", radius_list
        # print "Moons:", moon_list
        # print "Planets:", planet_list
        # print "Nr. Planets:", planetNr_list
        
        return [result_info, jcodes]


def main():
    # Development purposes
    epi = Epicenter("../../epicenter.db", "wormholes", "statics")
    print epi
    
if __name__ == '__main__':
    main()
