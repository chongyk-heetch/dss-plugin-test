from .. import env
import requests
from datetime import datetime
from import_csv_interface import ImportCsvInterface

##################################### Ops comment Action ####################################
class OpsCommentsAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'user_uid', 'type': 'str'}, {'col': 'comment', 'type': 'str'}]

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running OpsCommentsAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):
        uri = env.api_url + env.users_comments_endpoint.format(row['user_uid'])
        payload = {
            'operator': {
                'origin': 'app',
                'value': self.get_origin()
            },
            'message': row['comment'],
            'date': datetime.now().strftime("%Y-%m-%d"),
            'allow_duplicate': False  ## important otherwise, it will create same comment
        }

        print('POST uri={} payload={}'.format(uri, payload))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)
