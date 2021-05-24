from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from oauth2client.file import Storage
import json
import os
import re
import httplib2
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client
import requests
import pandas as pd

'''function check whether file exist in the path or not'''
def where_json(file_name): return os.path.exists(file_name)


''' function return the refresh token '''
def get_refresh_token(client_id, client_secret):
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
    REDIRECT_URI = 'http:localhost:8080'

    flow = OAuth2WebServerFlow(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPE, redirect_uri=REDIRECT_URI)
    if not where_json('credential.json'):
        storage = Storage('credential.json')
        credentials = run_flow(flow, storage)
        refresh_token = credentials.refresh_token

    elif where_json('credential.json'):
        with open('credential.json') as json_file:
            data = json.load(json_file)
        refresh_token = data['refresh_token']

    return refresh_token


# client_id = '125156429855-qsek7aknn45oqfg1u0jd3kl4nvnsuuib.apps.googleusercontent.com'
# client_secret = 'fgHg7vB4esriIXDi7KbaZJca'

client_id = '125156429855-1blgeq7btu6q1n40a8c4c6n7sd6ta4n5.apps.googleusercontent.com'
client_secret = 'xhtQB7Xqd53Eb8oQcpuraL7G'

refresh_token = get_refresh_token(client_id, client_secret)

''' function return the google analytics data for given dimension, metrics, start data, end data access token, type,goal number, condition'''


def google_analytics_reporting_api_data_extraction(viewID, dim, met, start_date, end_date, refresh_token,
                                                   transaction_type, goal_number, condition):
    viewID = viewID;
    dim = dim;
    met = met;
    start_date = start_date;
    end_date = end_date;
    refresh_token = refresh_token;
    transaction_type = transaction_type;
    condition = condition
    goal_number = goal_number
    viewID = "".join(['ga%3A', viewID])

    if transaction_type == "Goal":
        met1 = "%2C".join([re.sub(":", "%3A", i) for i in met]).replace("XX", str(goal_number))
    elif transaction_type == "Transaction":
        met1 = "%2C".join([re.sub(":", "%3A", i) for i in met])

    dim1 = "%2C".join([re.sub(":", "%3A", i) for i in dim])

    if where_json('credential.json') == True:
        with open('credential.json') as json_file:
            storage_data = json.load(json_file)

        client_id = storage_data['client_id']
        client_secret = storage_data['client_secret']
        credentials = client.OAuth2Credentials(
            access_token=None, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token,
            token_expiry=3600, token_uri=GOOGLE_TOKEN_URI, user_agent='my-user-agent/1.0', revoke_uri=GOOGLE_REVOKE_URI)

        credentials.refresh(httplib2.Http())
        rt = (json.loads(credentials.to_json()))['access_token']

        api_url = "https://www.googleapis.com/analytics/v3/data/ga?ids="

        url = "".join(
            [api_url, viewID, '&start-date=', start_date, '&end-date=', end_date, '&metrics=', met1, '&dimensions=',
             dim1, '&max-results=1000000', condition, '&access_token=', rt])

        data = pd.DataFrame()

        try:
            r = requests.get(url)

            try:
                data = pd.DataFrame(list((r.json())['rows']), columns=[re.sub("ga:", "", i) for i in dim + met])
                data['date'] = start_date
                print("data extraction is successfully completed")

                return data
            except:
                print((r.json()))
        except:
            print((r.json()))
            print("error occured in the google analytics reporting api data extraction")


viewID = '229095764'
dim = ['ga:source']
met = ['ga:users']
start_date = '2021-01-01'
end_date = '2021-01-10'
transaction_type = 'Transaction'
goal_number = ''
refresh_token = refresh_token
condition = ''

data = google_analytics_reporting_api_data_extraction(viewID, dim, met, start_date, end_date, refresh_token,
                                                      transaction_type, goal_number, condition)
