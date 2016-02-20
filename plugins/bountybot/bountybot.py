"""
Created on 2015-06-06

@author: Valtyr Farshield
"""

import random

from bountydb import BountyDb
from bountyconfig import BountyConfig
from bb_common import BbCommon
from masscalc.whmanager import WhManager


class BountyBot:
    def __init__(self, talk):
        # Slackbot output function
        self.talk = talk

        # Bounty Database initialization
        self.bountydb = BountyDb(
            "epicenter.db",
            "bounties.db",
            "wormholes",
            "generics",
            self.report_kill,
            self.report_thera,
            self.report_thera_generic,
            self.report_thera_tripnull,
            BountyConfig.INTERVAL,
            BountyConfig.WAIT,
            BountyConfig.CYCLE
        )
        whmanager = WhManager(self)

        # -----------------------------------------------------------------------------
        # Channel Settings
        self.ch = BountyConfig.get_channels()
        
        # Construct a list of channels where commands can be executed
        self.chlist_cfg = [self.ch["bountybot-config"]]
        self.chlist_all = [self.ch["wormhole-sales"], self.ch["testing"]] + self.chlist_cfg
        
        # Should Bounty Bot accept commands in direct channels?
        if BountyConfig.PM_ENABLED:
            self.chlist_all += "D"
        
        # Should Bounty Bot accept commands in private groups?
        if BountyConfig.PG_ENABLED:
            self.chlist_all += "G"
        
        # -----------------------------------------------------------------------------
        # Command section
        
        # Each command starts with one of the following prefixes:
        self.cmd_start = ["!bountybot", "!bounty", "!bb"]
        
        # Command configuration list
        self.cmd_list = [
            ["help", self.chlist_all, self.cbk_help, [
                ("", "displays this message")
            ]],
            ["about", self.chlist_all, self.cbk_about, [
                ("", "displays information about BountyBot and shows link to the manual")
            ]],
            ["hello", self.chlist_all, self.cbk_hello, [
                ("", "simple verification which tests if BountyBot is up and running")
            ]],
            ["check", self.chlist_all, self.cbk_check, [
                ("<jcode>", "verify if J-code is in the specific or generic orders list")
            ]],
            ["list", self.chlist_all, self.cbk_list, [
                (
                    "[generic/jcode/jcode+]",
                    "displays current bounty systems (systems with * symbol have kill reports disabled)"
                )
            ]],
            ["generic", self.chlist_all, self.cbk_generic, [
                ("<id>", "displays J-codes associated with generic of specified ID")
            ]],
            ["info", self.chlist_all, self.cbk_info, [
                ("<jcode>", "displays characteristics of a wormhole")
            ]],
            ["search", self.chlist_all, self.cbk_search, [
                ("<description>", "displays J-codes which match the description")
            ]],
            ["static", self.chlist_all, self.cbk_static, [
                ("<code>", "displays information on a static code (ex. D382)")
            ]],
            # -----------------------------------------------------------------------------
            ["add", self.chlist_cfg, self.cbk_add, [
                (
                    "<jcode> <watchlist> <comments>",
                    "add new bounty system to database; <watchlist> must be either true or false"
                ),
                ("generic <description>", "add new generic bounty system")
            ]],
            ["remove", self.chlist_cfg, self.cbk_remove, [
                ("<jcode>", "remove bounty system from Watch List"),
                ("generic <id>", "remove generic bounty system")
            ]],
            ["edit", self.chlist_cfg, self.cbk_edit, [
                (
                    "<jcode> <watchlist> [new_comments]",
                    "modify the comments of a specific wormhole; <watchlist> must be either true or false"
                ),
                (
                    "generic <id> <new_description>",
                    "modify the description of a generic wormhole"
                )
            ]],
            ["destroy", self.chlist_cfg, self.cbk_destroy, [
                ("[generic/jcode]", "CAUTION! removes all [generic/jcode] bounty systems")
            ]],
            ["echo", self.chlist_cfg, self.cbk_echo, [
                ("<channel> <message>", "send a message as Bounty Bot")
            ]],
            ["announce", self.chlist_cfg, self.cbk_announce, [
                ("<message>", "make an announcement as Bounty Bot")
            ]],
            # -----------------------------------------------------------------------------
            ["spawn", self.chlist_all, whmanager.cbk_spawn, [
                ("", "view spawned wormholes in current channel"),
                ("<sig> <type> <state>", "spawn a wormhole")
            ]],
            ["splash", self.chlist_all, whmanager.cbk_splash, [
                ("<sig> <ship_mass>", "splash a wormhole with specified ship mass"),
            ]],
            ["shrink", self.chlist_all, whmanager.cbk_shrink, [
                ("<sig>", "report when wormhole shrinks"),
            ]],
            ["collapse", self.chlist_all, whmanager.cbk_collapse, [
                ("<sig>", "remove wormhole from channel"),
            ]],
            ["chance", self.chlist_all, whmanager.cbk_chance, [
                ("<sig> <ship_mass>", "compute probability of wormhole collapse with specified ship mass"),
            ]],
        ]
        self.talk(self.ch["general"], "Back online")
        self.talk(self.ch["wormhole-sales"], "Back online")
    
    # Command Interpreter
    def process_cmd(self, data):
        cmd_args = data["text"].split()
        
        # Check if the message is addressed to Bounty Bot
        if cmd_args[0].lower() in self.cmd_start:
            
            # Is it a valid command - at least one argument and command should be in list?
            cmd_found = False
            if len(cmd_args) > 1:
                for cmd in self.cmd_list:
                    if cmd_args[1].lower() == cmd[0]:
                        cmd_found = True
                        
                        # Make sure the command is executed from the correct channel
                        if any(data["channel"].startswith(item) for item in cmd[1]):
                            cmd[2](data["channel"], cmd_args[2:])  # ignore the first 2 arguments
                        else:
                            self.talk(
                                data["channel"],
                                "Command '{}' can not be executed from this channel".format(cmd_args[1])
                            )
            
                if not cmd_found:
                    # command not in list
                    self.talk(
                        data["channel"],
                        "No such command '{}'. Type '!bb help' from a Bounty Bot channel for more info".format(
                            cmd_args[1]
                        )
                    )
            
            else:
                # no argument specified
                self.talk(
                    data["channel"],
                    "Please specify at least one argument. Type '!bb help' from a Bounty Bot channel for more info"
                )
    
    # Report-A-Kill callback
    def report_kill(self, wormhole):
        message = "{} - Kill detected at {} https://zkillboard.com/system/{}/ Info: {}".format(
            wormhole.name,
            wormhole.lastkillDate,
            wormhole.sysId,
            wormhole.comments
        )
        self.talk(self.ch["bountybot-report"], message)

    # Report Thera specific wormhole connection
    def report_thera(self, wormhole):
        message = "`[THERA]` Connection to *{}* detected! Info: {}".format(
            wormhole.name,
            wormhole.comments
        )
        self.talk(self.ch["bountybot-report"], message)

    # Report Thera generic wormhole connection
    def report_thera_generic(self, generic_wh, th_sys):
        message = "`[THERA]` Generic wormhole *#{}* detected: *{}*".format(
            generic_wh.idx,
            th_sys
        )
        self.talk(self.ch["wormhole-sales"], message)

    # Report Thera generic wormhole connection
    def report_thera_tripnull(self, th_sys):
        message = "`[THERA]` Psst! Tripnull connection detected: *{}*".format(
            th_sys
        )
        self.talk(self.ch["wormhole-sales"], message)
    
    # -----------------------------------------------------------------------------
    # Command callbacks
       
    # !bb help
    def cbk_help(self, channel, _):
        message = "Commands may start with one of the following: "
        message += "  ".join(self.cmd_start) + "\n"
        
        for cmd in self.cmd_list:
            # Only display commands which can be executed from current channel
            if any(channel.startswith(item) for item in cmd[1]):
                for cmd_flavour in cmd[3]:
                    message += ">`" + self.cmd_start[0] + " " + cmd[0] + " " + cmd_flavour[0] + "`  -- " + \
                               cmd_flavour[1] + "\n"

        self.talk(channel, message)
    
    # !bb about
    def cbk_about(self, channel, _):
        message = "-- Wingspan Bounty Bot --\n"
        message += ">My purpose is to report kills which take place in bounty wormhole systems ^^\n"
        message += ">My code is based upon: https://github.com/farshield/bountybot\n"
        message += ">You can read my manual at this link: " + BountyConfig.RTFM
        self.talk(channel, message)
    
    # !bb hello
    def cbk_hello(self, channel, _):
        hi_msg = [
            "Hello :)", "Hi :P", "Hey", "Kill all humans!", "Howdy ;)", "Hola =)", "What's up?", "Hey o7",
            "o/", "o7", "\o", "Hey, buddy"
        ]
        self.talk(channel, random.choice(hi_msg))
    
    # !bb check
    def cbk_check(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            message_list = []
            name_list = cmd_args[0:BountyConfig.MAX_PARAMETER]
            
            for name in name_list:
                # check if the system with the specified name even exists
                if self.bountydb.valid_wormhole(name):
                    
                    # display characteristics of the wormhole, too
                    output_message = self.bountydb.compact_info_jcode(name) + "\n"
                    
                    # verify if J-code is in the specific order list
                    wh = self.bountydb.get_jcode(name)
                    if wh is not None:
                        output_message += ">`Found!` " + str(wh)
                    else:
                        output_message += ">*{}* not in specific orders list".format(name.upper())
                    output_message += "\n"
                    
                    # verify if J-code is in the generic order list
                    match_list = self.bountydb.verify_generic(name)
                    if match_list:
                        generic_message = ">`Found!` *{}* in generic order(s) ".format(name.upper())
                        
                        for generic_idx in match_list:
                            generic_message += "#{} ".format(generic_idx)
                        
                        output_message += generic_message
                    else:
                        output_message += ">*{}* not in generic orders list".format(name.upper())
                        
                    message_list.append(output_message)
                
                else:
                    message_list.append("'{}' - no such wormhole in Eve database. Recheck the spelling.".format(name))
            
            self.talk(channel, "\n".join(message_list))  # final message
        
        else:
            self.talk(channel, BountyBot.invalid_arg("check", 1))

    # !bb list
    def cbk_list(self, channel, cmd_args):
        if len(cmd_args) == 0:
            message = self.__list_generic()
            message += "\n"
            message += self.__list_jcode()
        else:
            if cmd_args[0].lower() in ["generic", "generics"]:
                message = self.__list_generic()
            elif cmd_args[0].lower() in ["jcode", "jcodes"]:
                message = self.__list_jcode()
            elif cmd_args[0].lower() in ["jcode+", "jcodes+"]:
                message = self.__list_jcode_detail()
            else:
                message = BountyBot.cmd_error("list", "2nd argument must be either 'generic', 'jcode' or 'jcode+'")
        
        self.talk(channel, message)

    # !bb jcodes
    def cbk_generic(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            idx = cmd_args[0]
            
            if BbCommon.represents_int(idx):
                # -----------------------------------------------------------------------------
                idx = int(idx)
                jcodes = self.bountydb.generic_jcodes(idx)
                if jcodes is not None:
                    if jcodes:
                        message = "Matches: {}.".format(len(jcodes))
                        
                        if len(jcodes) > BountyConfig.SEARCH_RESULTS:
                            message += " Results limited to {}.".format(BountyConfig.SEARCH_RESULTS)
                        
                        message += "```"
                        message += " ".join(jcodes[:BountyConfig.SEARCH_RESULTS])
                        message += "```"
                    
                    else:
                        message = "Generic #{} has no associated J-codes".format(idx)
                else:
                    message = "Generic #{} is not in list".format(idx)
                # -----------------------------------------------------------------------------
            else:
                message = BountyBot.cmd_error("generic", "'{}' is not a number".format(idx))
                
            # display result of operation
            self.talk(channel, message)
        else:
            self.talk(channel, BountyBot.invalid_arg("generic", 1))

    # !bb info
    def cbk_info(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            message_list = []
            
            name_list = cmd_args[0:BountyConfig.MAX_PARAMETER]
            for name in name_list:
                message_list.append(self.bountydb.info_jcode(name))
            
            self.talk(channel, "\n".join(message_list))
        else:
            self.talk(channel, BountyBot.invalid_arg("info", 1))

    # !bb search
    def cbk_search(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            description = " ".join(cmd_args)
            [result_info, jcodes] = self.bountydb.search_generic(description)
            
            message = result_info
            if len(jcodes) > BountyConfig.SEARCH_RESULTS:
                message += " Results limited to {}.".format(BountyConfig.SEARCH_RESULTS)
            
            if len(jcodes) > 0:
                message += "```"
                message += " ".join(jcodes[:BountyConfig.SEARCH_RESULTS])
                message += "```"
                    
            self.talk(channel, message)
        else:
            self.talk(channel, BountyBot.invalid_arg("search", 1))

    # !bb static
    def cbk_static(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            static_code = cmd_args[0]
            message = self.bountydb.search_static(static_code)
            self.talk(channel, message)
        else:
            self.talk(channel, BountyBot.invalid_arg("static", 1))

    # !bb add
    def cbk_add(self, channel, cmd_args):
        if len(cmd_args) >= 2:
            # add a generic wormhole
            if cmd_args[0].lower() == "generic":
                description = " ".join(cmd_args[1:])
                [message, result_info] = self.bountydb.add_generic(description)
                self.talk(channel, result_info)
            
            # add a specific J-code
            else:
                if len(cmd_args) >= 3:
                    name = cmd_args[0]
                    
                    if cmd_args[1].lower() == "true":
                        watchlist = True
                    elif cmd_args[1].lower() == "false":
                        watchlist = False
                    else:
                        watchlist = None
                    
                    comments = " ".join(cmd_args[2:])
                    
                    if watchlist is not None:
                        message = self.bountydb.add_jcode(name, watchlist, comments)
                    else:
                        message = BountyBot.cmd_error("add", "2nd argument 'watchlist' must be either true or false")
                else:
                    message = BountyBot.cmd_error(
                        "add",
                        "at least 3 arguments have to be specified when adding a specific wormhole"
                    )
        
            # display result of operation
            self.talk(channel, message)
            print "[Op] Add:", message
        else:
            self.talk(channel, BountyBot.invalid_arg("add", 2))
    
    # !bb remove
    def cbk_remove(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            # remove a generic wormhole
            if cmd_args[0].lower() == "generic":
                if len(cmd_args) >= 2:
                    idx = cmd_args[1]
                    if BbCommon.represents_int(idx):
                        idx = int(idx)
                        message = self.bountydb.remove_generic(idx)
                    else:
                        message = BountyBot.cmd_error("remove", "'{}' is not a number".format(idx))
                else:
                    message = BountyBot.cmd_error("remove", "generic removal must have another argument <id>")
            
            # remove a specific J-code
            else:
                name = cmd_args[0]
                message = self.bountydb.remove_jcode(name)
            
            # display result of operation
            self.talk(channel, message)
            print "[Op] Remove:", message
        else:
            self.talk(channel, BountyBot.invalid_arg("remove", 1))

    # !bb edit
    def cbk_edit(self, channel, cmd_args):
        if len(cmd_args) >= 2:
    
            # edit a generic wormhole
            if cmd_args[0].lower() == "generic":
                if len(cmd_args) >= 3:
                    idx = cmd_args[1]
                    if BbCommon.represents_int(idx):
                        idx = int(idx)
                        description = " ".join(cmd_args[2:])
                        [message, result_info] = self.bountydb.edit_generic(idx, description)
                        if result_info != "":
                            self.talk(channel, result_info)
                    else:
                        message = BountyBot.cmd_error("edit", "'{}' is not a number".format(idx))
                else:
                    message = BountyBot.cmd_error("edit", "generic editing must have an <id> and a <new_description>")
    
            # edit a specific wormhole
            else:
                name = cmd_args[0]
                
                if cmd_args[1].lower() == "true":
                    watchlist = True
                elif cmd_args[1].lower() == "false":
                    watchlist = False
                else:
                    watchlist = None
                
                comments = " ".join(cmd_args[2:])
                
                if watchlist is not None:
                    message = self.bountydb.edit_jcode(name, watchlist, comments)
                else:
                    message = BountyBot.cmd_error("edit", "2nd argument 'watchlist' must be either true or false")
    
            # display result of operation
            self.talk(channel, message)
            print "[Op] Edit:", message
        else:
            self.talk(channel, BountyBot.invalid_arg("edit", 2))
    
    # !bb destroy
    def cbk_destroy(self, channel, cmd_args):
        if len(cmd_args) == 0:
            self.bountydb.clear_generic()
            self.bountydb.clear_jcode()
            message = "Generic and J-code lists have been cleared"
        else:
            if cmd_args[0].lower() in ["generic", "generics"]:
                self.bountydb.clear_generic()
                message = "Generic list has been cleared"
            elif cmd_args[0].lower() in ["jcode", "jcodes"]:
                self.bountydb.clear_jcode()
                message = "J-code list has been cleared"
            else:
                message = BountyBot.cmd_error("destroy", "2nd argument must be either 'generic' or 'jcode'")
        
        # display result of operation
        self.talk(channel, message)
        print "[Op] Clear:", message

    # !bb echo
    def cbk_echo(self, channel, cmd_args):
        if len(cmd_args) >= 2:
            target_channel = cmd_args[0]
            target_msg = " ".join(cmd_args[1:])
            
            if target_channel in self.ch.keys():
                self.talk(self.ch[target_channel], target_msg)
            else:
                self.talk(channel, BountyBot.cmd_error("echo", "invalid channel name"))
        else:
            self.talk(channel, BountyBot.invalid_arg("echo", 2))
    
    # !bb announce
    def cbk_announce(self, channel, cmd_args):
        if len(cmd_args) >= 1:
            target_msg = " ".join(cmd_args[0:])
            self.talk(self.ch["general"], target_msg)
            self.talk(self.ch["wormhole-sales"], target_msg)
        else:
            self.talk(channel, BountyBot.invalid_arg("announce", 1))

    # -----------------------------------------------------------------------------
    # Helper functions

    # List only generic wormholes
    def __list_generic(self):
        message = "Generic orders:\n"
        generic_list = self.bountydb.list_generic()
        
        if len(generic_list) > 0:
            for wh_gen in generic_list:
                message += ">" + str(wh_gen) + "\n"
        else:
            message = "Generic wormhole list is empty"
        
        return message
    
    # List short J-codes
    def __list_jcode(self):
        output_list = []
        jcode_list = self.bountydb.list_jcode()
        
        if len(jcode_list) > 0:
            for wh in jcode_list:
                wh_element = "*{}* [C{}]".format(wh.name, wh.whclass)
                if not wh.watchlist:
                    wh_element += "~"  # append special character to denote system is not actively watchlisted
                output_list += [wh_element]
                
            message = "Specific orders:\n>" + ", ".join(output_list)
        else:
            message = "J-code list is empty"
            
        return message
    
    # List J-codes with details
    def __list_jcode_detail(self):
        message = ""
        jcode_list = self.bountydb.list_jcode()
        
        if len(jcode_list) > 0:
            for wh in self.bountydb.list_jcode():
                message += str(wh) + "\n"
        else:
            message = "J-code list is empty"
            
        return message

    # Called when a command has incorrect number arguments
    @staticmethod
    def invalid_arg(cmd_name, nr_args):
        return "Command '{}' not called correctly: at least {} additional argument(s) has(have) to be specified".format(
            cmd_name, nr_args
        )

    @staticmethod
    # Called when a command does not have valid arguments
    def cmd_error(cmd_name, msg):
        return "Error executing '{}': {}".format(cmd_name, msg)

    # -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Development purposes
    pass
