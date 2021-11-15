from .. import env
import requests
from action_interface import ActionInterface
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import math
import numpy as np


##################################### Assign canvas to passenger Action ####################################
class CanvasPassengerAction(ActionInterface):
    def __init__(self,
                 df_name,
                 df,
                 token):
        # because it s python 2.7
        ActionInterface.__init__(self,
                                 df_name,
                                 df,
                                 token)
        # Use this attribute to validate schema
        # Order does not matter
        self._df_cols = [{'col': 'passenger_id', 'type': 'str'}, {'col': 'canvas_id', 'type': 'str'}]

        # add okta robot in headers
        self.okta_auth = True

    @staticmethod
    def get_number_slice(nb_elements):
        return math.trunc(nb_elements / 100) + 1

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_passenger = []
        for chunk in np.array_split(self.df, self.get_number_slice(len(self.df.index))):
            try:
                r = self.post_request(chunk)
                if (500 <= r.status_code <= 599):
                    raise requests.exceptions.RequestException(r.status_code)
                print('POST status = {}'.format(r.status_code))
            except requests.exceptions.RequestException as e:
                print('[Error]', e)

        errors_passenger_df = pd.DataFrame(errors_passenger)
        errors_passenger_dataset_name = self.create_errors_dataset(errors_passenger_df)

        if not errors_passenger_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_passenger_dataset_name))

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running CanvasPassengerAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, chunk):
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        uri = env.api_url + env.canvas_passenger_endpoint.format(chunk['canvas_id'].iloc[0])
        payload = {
            'passenger_ids': chunk['passenger_id'].tolist()
        }

        print('POST uri={} payload={}'.format(uri, payload, self.get_headers()))
        resp = session.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)
        return resp
