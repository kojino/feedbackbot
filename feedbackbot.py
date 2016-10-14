import os
import time
from slackclient import SlackClient
import mysql.connector
import config

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
# constants
AT_BOT = "<@" + BOT_ID + ">"
# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# list of instructors eligible for receiving messages
instructors = ["tlambrou", "kojin","braus","alan","nikolas","shannon","mitchell"]

def store_data(sender_name,instructor,feedback):
    # store feedback
    cursor = cnx.cursor()
    data = [sender_name,instructor,feedback,time.strftime('%Y-%m-%d %H:%M:%S')]
    data_log = tuple(data)
    update_log=("INSERT INTO feedbacks (sender,recipient,feedback_text,date_sent) VALUES (%s,%s,%s,%s)")
    cursor.execute(update_log, data_log)
    cnx.commit()
    print "data stored"
    cursor.close()

def get_sender_name(channel):
    # get all direct messages
    ims = slack_client.api_call("im.list")["ims"]
    # check if the feedback is sent from a direct message
    for im in ims:
        if channel == im["id"]:
            # find the user who sent the feedback
            user = im["user"]
            name = slack_client.api_call("users.info", user=user)["user"]["name"]
            return name
    return ""

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Enter your feedback in the format 'instructor_name: feedback_content'"
    # separate the command
    feedback_array = command.split(":")
    instructor = feedback_array[0]
    feedback = ":".join(feedback_array[1:])

    instructor_valid = instructor in instructors
    sender_name = get_sender_name(channel)

    # send and store feedback only if user was found in a direct message
    if instructor_valid:
        if sender_name != "":
        # send feedback
            instructor = "@"+instructor
            template = "You have a new feedback: "
            slack_client.api_call("chat.postMessage", channel=instructor,
                                    text=template + feedback, as_user=True)
            store_data(sender_name,instructor,feedback)
            response = "Your feedback is sent to %s :) " % instructor
        else:
            response = "You can only send feedbacks as direct messages to me."
    # reply to the sender
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    cnx = mysql.connector.connect(**config.db_info) # connect to database
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                print channel
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
    cnx.close()
