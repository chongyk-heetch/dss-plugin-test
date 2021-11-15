from .. import env
import requests
import pandas as pd
from import_csv_interface import ImportCsvInterface

##################################### Passenger Unsuspention Action ####################################
class PassengerUnsuspentionAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'passenger_profile_id', 'type': 'str'}]

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_suspension = []
        for index, row in self.df.iterrows():
            try:
                r = self.post_request(row)
                if not (200 <= r.status_code <= 299) and not r.status_code == 409:
                    raise requests.exceptions.RequestException(r.status_code)
                print('POST status = {}'.format(r.status_code))
            except requests.exceptions.RequestException as e:
                print('[Error]', e)
                row['error'] = e
                errors_suspension.append(row)


        errors_suspension_df = pd.DataFrame(errors_suspension)
        errors_suspension_dataset_name = self.create_errors_dataset(errors_suspension_df)

        if not errors_suspension_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_suspension_dataset_name))

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running PassengerUnsuspentionAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):

        uri = env.api_url + env.passenger_unsuspension_endpoint

        payload = {
            'passenger_profile_id': row['passenger_profile_id']
        }

        print('POST uri={} payload={}'.format(uri, payload, self.get_headers()))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)