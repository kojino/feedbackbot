import httplib2
import urllib
import json
import os

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')

class SlackAPI:
    # Variables
    BASE_URL = "https://slack.com/api/"
    instructors = ["kojin","braus","alan","nikolas","shannon","mitchell"]

    # Init
    def __init__(self, token):
    	self.token = token

    # def users(self):
    #     args = {'token': self.token}
    #     return self.__request("users.list","GET",**args)

    def message(self,user):
        if user not in SlackAPI.instructors:
            return "Invalid instructor"
        else:
            args = {"token": self.token,
                    "channel": "@kojin",
                    "text": "hello world"}
            self.__request("chat.postMessage","POST",**args)

    # Google Translate Request
    def __request(self, path, method, **args):
        data = urllib.urlencode(args)
    	url = SlackAPI.BASE_URL + path + "?" + data
        print url
    	http = httplib2.Http()
    	response, content = http.request(url, method)
    	return(content)

    # Parse the JSON
    def __parse_json(self, json_string):
    	data_dict = json.loads(json_string)
    	try:
    		translated_text = data_dict['data']['translations'][0]['translatedText']
    	except:
    		translated_text = "The text could not be translated."
    	return(translated_text)

if __name__ == "__main__":
    slackbot = SlackAPI("xoxb-88403603223-qzn55jPQnvFYTqz0AsKdNp04")
    print slackbot.message("kojin")
