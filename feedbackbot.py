import os
import time
from slackclient import SlackClient
import mysql.connector

# Amazon RDS db info
config = {
'user': 'admin',
'password': 'MSbot2016',
'database': 'feedbacks',
'host': 'msbot-cluster-1.cluster-cpo2bflrumwo.us-east-1.rds.amazonaws.com',
'port': '3306'}

cnx = mysql.connector.connect(**config)


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "send feedback"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
instructors = ["feedback", "kojin","braus","alan","nikolas","shannon","mitchell"]

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Enter your feedback in the format 'instructor_name: feedback_content'"
    feedback_array = command.split(":")
    instructor = feedback_array[0]
    feedback = ":".join(feedback_array[1:])
    if instructor in instructors:
        if instructor == "feedback_test":
            slack_client.api_call("chat.postMessage", channel="#"+instructor,
                                    text=feedback, as_user=True)
            instructor = "#"+instructor
        else:
            slack_client.api_call("chat.postMessage", channel="@"+instructor,
                                    text=feedback, as_user=True)
            instructor = "@"+instructor
        slack_client.api_call("channels.info", channel=channel)
        cursor = cnx.cursor()
        data = [channel,instructor,feedback,time.time()]
        data_log = tuple(data)
        update_log=("INSERT INTO feedbacks (sender,recipient,feedback_text,date_sent) VALUES (%s,%s,%s,%s)")
        cursor.execute(update_log, data_log)
        cnx.commit()
        print "data stored"
        cursor.close()
        response = "Your feedback is sent to %s :) " % instructor
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
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
cnx.close()
