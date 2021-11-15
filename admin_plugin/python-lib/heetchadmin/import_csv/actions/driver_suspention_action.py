from .. import env
import requests
from import_csv_interface import ImportCsvInterface


##################################### Driver Suspention Action ####################################
class DriverSuspentionAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'driver_uid', 'type': 'str'}, {'col': 'never_again', 'type': 'bool'},
                         {'col': 'reason_id', 'type': 'str'}, {'col': 'comment', 'type': 'str'},
                         {'col': 'reactivation_cta_url', 'type': 'str'}]

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running DriverSuspentionAction ...')
        self.validate_dataset()
        self.post_data()


        
    def post_request(self, row):
        uri = env.api_url + env.driver_suspension_endpoint.format(row['driver_uid'])

        payload = {
            'operator': {
                'origin': 'app',
                'value': self.get_origin()
            },
            'never_again': row['never_again'],
            'reason': row['reason_id'],
            'message': row['comment']
        }
        
        if not self.isNaN(row['reactivation_cta_url']):
            payload['reactivation_cta_url'] = row['reactivation_cta_url'] 

        print('POST uri={} payload={}'.format(uri, payload, self.get_headers()))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)

