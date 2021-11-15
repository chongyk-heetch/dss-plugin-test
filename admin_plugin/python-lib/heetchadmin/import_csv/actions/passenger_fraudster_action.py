from .. import env
import requests
from datetime import datetime
import pandas as pd
from payload_builder import to_users_comments_payload
from import_csv_interface import ImportCsvInterface
import json

##################################### Passenger Fraudster Action ####################################
class PassengerFraudsterAction(ImportCsvInterface):
    def __init__(self,
                 df_name,
                 df,
                 token,
                 process):
        # because it s python 2.7
        ImportCsvInterface.__init__(self,
                                 df_name,
                                 df,
                                 token,
                                 process)

        # Use this attribute to validate schema
        # Order does not matter
        self._df_cols = [{'col': 'user_id', 'type': 'str'}, {'col': 'is_fraudster', 'type': 'boolean'},
                         {'col': 'comment', 'type': 'str'}]
        
    def get_headers(self):
        headers = {
            'Authorization': 'Token:' + self.token,
            'Content-Type': 'application/json',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept': 'application/json,application/vnd.heetch;ver=3'
        }
        return headers

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_fraudster = []
        errors_comment = []
        for index, row in self.df.iterrows():
            try:
                r = self.post_request(row)
                if not (200 <= r.status_code <= 299) and not r.status_code == 409:
                    raise requests.exceptions.RequestException(r.status_code)
                print('POST status = {}'.format(r.status_code))
                
                if (200 <= r.status_code <= 299):
                    # Split here to handle each endpoint errors
                    try:
                        r = self.post_request_comment(row)
                        r.raise_for_status()
                        print('POST status = {}'.format(r.status_code))
                    except requests.exceptions.RequestException as e:
                        print('[Error]', e)
                        row['error'] = e
                        errors_comment.append(row)
            except requests.exceptions.RequestException as e:
                print('[Error]', e)
                row['error'] = e
                errors_fraudster.append(row)

        errors_fraudster_df = pd.DataFrame(errors_fraudster)
        errors_fraudster_dataset_name = self.create_errors_dataset(errors_fraudster_df)

        errors_comment_df = pd.DataFrame(errors_comment)
        errors_comment_dataset_name = self.create_errors_dataset(errors_comment_df)

        if not errors_fraudster_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_fraudster_dataset_name))

        if not errors_comment_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_comment_dataset_name))

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running PassengerFraudsterAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):

        uri = env.api_url + env.passenger_fraudster_endpoint.format(row['user_id'])

        payload = {
            'operator': {
                'origin': 'app',
                'value': self.get_origin()
            },
            'fraudster': row['is_fraudster']
        }

        print('POST uri={} payload={}'.format(uri, json.dumps(payload), self.get_headers()))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)

    def post_request_comment(self, row):

        uri = env.api_url + env.users_comments_endpoint.format(row['user_id'])
        payload = to_users_comments_payload(self.get_origin(), row['comment'], datetime.now().strftime("%Y-%m-%d"))

        print('POST uri={} payload={}'.format(uri, payload))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)


