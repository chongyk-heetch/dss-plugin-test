from .. import env
import requests
from import_csv_interface import ImportCsvInterface

##################################### Ride comment Action ####################################
class RideCommentsAction(ImportCsvInterface):
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
        self._df_cols = [{'col': 'ride_uid', 'type': 'str'}, {'col': 'comment', 'type': 'str'}]

    def run(self):
        print('Running on API : {}'.format(env.api_url))
        print('Running RideCommentsAction ...')
        self.validate_dataset()
        self.post_data()

    def post_request(self, row):
        uri = env.api_url + env.ride_comments_endpoint

        hashtags = []

        tags = row['hashtags'].split(',')

        for tag in tags:
            hashtags.append({'name': tag})

        payload = {
            'resource_id': row['ride_uid'],
            'author_origin': 'app',
            'author_value': self.get_origin(),
            'message': row['comment'],
            'hashtags': hashtags
        }

        print('POST uri={} payload={}'.format(uri, payload))
        return requests.request("POST", uri, headers=self.get_headers(), json=payload, timeout=30)

