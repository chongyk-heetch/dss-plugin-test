from .. import env
import requests
import pandas as pd
from action_interface import ActionInterface

##################################### Ride comment Action ####################################
class ProdcutLinesAssignAction(ActionInterface):
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
        self._df_cols = [{'col': 'driver_uid', 'type': 'str'}, {'col': 'product_line', 'type': 'str'}]
        
        # add okta robot in headers
        self.okta_auth = False

    def post_request(self, row):
        uri = env.api_url + env.product_lines_assignment_endpoint.format(row['driver_uid'], row['product_line'])

        payload = {}
        
        print('POST uri={} payload={}'.format(uri, payload, self.get_headers()))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)
        
    def post_data(self):
        errors_array = []
        for index, row in self.df.iterrows():
            try:
                r = self.post_request(row)
                if str(r.status_code).startswith("5"):
                    raise requests.exceptions.RequestException(r.status_code)
                print('POST status = {}'.format(r.status_code))
            except requests.exceptions.RequestException as e:
                print('[Error]', e)
                row['error'] = e
                errors_array.append(row)

        errors_df = pd.DataFrame(errors_array)
        errors_dataset_name = self.create_errors_dataset(errors_df)

        if not errors_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_dataset_name))
        
    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running ProductLinesAssignAction ...')
        self.validate_dataset()
        self.post_data()





