"""
Created on 2016-01-22

@author: Valtyr Farshield
"""

from wormholecrit import WormholeCrit


def represents_float(s):
    """
    Verifies if the string 's' is a float
    :param s: input string
    :return: True if 's' is a float
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


class WhManager:

    def __init__(self, bountybot):
        self.whlist = []
        self.talk = bountybot.talk
        self.invalid_arg = bountybot.invalid_arg
        self.cmd_error = bountybot.cmd_error
        self.bountydb = bountybot.bountydb

    def present_signature(self, channel, signature):
        for [ch, sig, _] in self.whlist:
            if ch == channel and sig == signature:
                return True

        return False

    def cbk_spawn(self, channel, cmd_args):
        """
        !bb spawn
        :param channel:
        :param cmd_args:
        :return:
        """
        if len(cmd_args) == 0:
            message = ""
            for [ch, sig, wh] in self.whlist:
                if ch == channel:
                    message += "Signature `{}`: {}\n".format(sig, str(wh))

            if message == "":
                message = "No wormholes spawned in this channel"

        elif len(cmd_args) >= 3:
            # spawn a new wormhole
            signature = cmd_args[0].upper()
            wh_code = cmd_args[1]
            wh_state = cmd_args[2].lower()

            if not self.present_signature(channel, signature):
                [maxmass, maxjump] = self.bountydb.static_mass(wh_code)
                if maxmass > 0 and maxjump > 0:
                    if wh_state == "new":
                        wh_state_id = WormholeCrit.NEW
                    elif wh_state == "stable":
                        wh_state_id = WormholeCrit.STABLE
                    elif wh_state == "unstable":
                        wh_state_id = WormholeCrit.DESTAB
                    elif wh_state == "critical":
                        wh_state_id = WormholeCrit.CRIT
                    else:
                        wh_state_id = WormholeCrit.COLLAPSED

                    if wh_state_id != WormholeCrit.COLLAPSED:
                        spawned_wormhole = WormholeCrit(maxmass, maxjump, wh_state_id)
                        self.whlist.append([channel, signature, spawned_wormhole])
                        message = "Signature `{}` added. {}".format(signature, str(spawned_wormhole))
                    else:
                        message = self.cmd_error(
                            "spawn", "'{}' is not a valid state. Try: new, stable, unstable, critical".format(wh_state)
                        )

                else:
                    message = self.cmd_error("spawn", "'{}' is not a wormhole code".format(wh_code))

            else:
                message = self.cmd_error("spawn", "'{}' is already present in this channel".format(signature))

        else:
            message = self.invalid_arg("spawn", 3)

        self.talk(channel, message)

    def cbk_splash(self, channel, cmd_args):
        """
        !bb splash
        :param channel:
        :param cmd_args:
        :return:
        """
        self.talk(channel, "Splash")

    def cbk_shrink(self, channel, cmd_args):
        """
        !bb shrink
        :param channel:
        :param cmd_args:
        :return:
        """

        self.talk(channel, "Shrink")

    def cbk_collapse(self, channel, cmd_args):
        """
        !bb collapse
        :param channel:
        :param cmd_args:
        :return:
        """
        if len(cmd_args) >= 1:
            signature = cmd_args[0].upper()

            message = ""
            for item in self.whlist:
                [ch, sig, _] = item

                if ch == channel and sig == signature:
                    self.whlist.remove(item)
                    message = "Wormhole with signature `{}` has been collapsed".format(signature)

            if message == "":
                message = "No wormhole with signature `{}` was found".format(signature)
        else:
            message = self.invalid_arg("collapse", 1)

        self.talk(channel, message)

    def cbk_chance(self, channel, cmd_args):
        """
        !bb chance
        :param channel:
        :param cmd_args:
        :return:
        """
        if len(cmd_args) >= 2:
            signature = cmd_args[0].upper()

            if represents_float(cmd_args[1]):
                ship_mass = float(cmd_args[1])

                message = ""
                for [ch, sig, wh] in self.whlist:
                    if ch == channel and sig == signature:
                        [plausible, chance] = wh.collapse_chance(ship_mass)

                        if plausible:
                            message = "Signature `{}`: chance of collapse is `{:.2f}%`".format(signature, chance)
                        else:
                            message = "A ship mass of `{} kT` can not jump the wormhole".format(ship_mass)

                if message == "":
                    message = "No wormhole with signature `{}` was found".format(signature)
            else:
                message = self.cmd_error("chance", "'{}' is not a valid ship mass".format(cmd_args[1]))

        else:
            message = self.invalid_arg("chance", 2)

        self.talk(channel, message)
