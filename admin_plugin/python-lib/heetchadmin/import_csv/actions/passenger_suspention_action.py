from .. import env
import requests
from datetime import datetime
import pandas as pd
from payload_builder import to_users_comments_payload
from import_csv_interface import ImportCsvInterface


##################################### Passenger Suspention Action ####################################
class PassengerSuspentionAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'passenger_profile_id', 'type': 'str'}, {'col': 'passenger_uid', 'type': 'str'},
                         {'col': 'reason', 'type': 'str'}, {'col': 'comment', 'type': 'str'}]

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_suspension = []
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
                errors_suspension.append(row)

        errors_suspension_df = pd.DataFrame(errors_suspension)
        errors_suspension_dataset_name = self.create_errors_dataset(errors_suspension_df)

        errors_comment_df = pd.DataFrame(errors_comment)
        errors_comment_dataset_name = self.create_errors_dataset(errors_comment_df)

        if not errors_suspension_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_suspension_dataset_name))

        if not errors_comment_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_comment_dataset_name))

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running PassengerSuspentionAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):

        uri = env.api_url + env.passenger_suspension_endpoint

        payload = {
            'passenger_profile_id': row['passenger_profile_id'],
            'reason_id': row['reason']
        }

        print('POST uri={} payload={}'.format(uri, payload, self.get_headers()))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)

    def post_request_comment(self, row):

        uri = env.api_url + env.users_comments_endpoint.format(row['passenger_uid'])
        payload = to_users_comments_payload(self.get_origin(), row['comment'], datetime.now().strftime("%Y-%m-%d"))

        print('POST uri={} payload={}'.format(uri, payload))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)


