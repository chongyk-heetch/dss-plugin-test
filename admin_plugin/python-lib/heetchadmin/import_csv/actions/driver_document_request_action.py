from .. import env
import requests
import pandas as pd
from import_csv_interface import ImportCsvInterface


##################################### Driver Document Request Action ####################################
## https://github.com/heetch/universe/blob/master/src/services/admin/gateway/settings.yml#L645
## https://github.com/heetch/universe/blob/master/src/services/admin/gateway/docs/openapi.yaml#L19375
class DriverDocumentRequestAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'driver_uid', 'type': 'str'}, {'col': 'record_type_id', 'type': 'str'},
                         {'col': 'previous_record_id', 'type': 'str'}, {'col': 'expires_at', 'type': 'str'}]

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_suspension = []
        for index, row in self.df.iterrows():
            try:
                r = self.post_request(row)
                r.raise_for_status()
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
        print('Running DriverDocumentRequestAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):

        uri = env.api_url + env.driver_document_request_endpoint

        payload = {
            'driver_id': row['driver_uid'],
            'record_type_id': row['record_type_id'],
            'expires_at': row['expires_at']

        }
        if row['previous_record_id'] and row['previous_record_id'] != None and row['previous_record_id'] != '' and row[
            'previous_record_id'] == row['previous_record_id']:
            payload['previous_record_id'] = row['previous_record_id']

        headers = self.get_headers()
        headers['Heetch-Operator-Okta-Id'] = env.okta_user

        print('POST uri={} payload={}'.format(uri, payload, headers))
        return requests.request("POST", uri, headers=headers, json=payload, timeout=30)
