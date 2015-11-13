'''
Created on 2015-06-06

@author: Valtyr Farshield
'''

from bountybot import BountyBot

crontable = []
outputs = []

# Sends a message to a specified Slack channel
def talk(channel, message):
    outputs.append([channel, message])

# Bounty Bot handler
bb = BountyBot(talk)

# Event - connected to server
def process_hello(data):
    print "[Info] Bounty Bot connected to server"

# Event - message received
def process_message(data):
    #print data["channel"], data["text"]
    bb.process_cmd(data)
