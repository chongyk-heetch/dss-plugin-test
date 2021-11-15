from .. import env
import requests
import dataiku
import pandas as pd


##################################### Action Interface ####################################
class ActionInterface():

    def __init__(self,
                 df_name,
                 df,
                 token
                 ):
        self._df_name = df_name
        self._df = df
        self._token = token
        self.okta_auth = False

    @property
    def df_name(self):
        return self._df_name

    @df_name.setter
    def df_name(self, df_name):
        self._df_name = df_name

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    def get_headers(self):
        headers = {
            'Authorization': 'Token:' + self.token,
            'Content-Type': 'application/json',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept': 'application/json,application/vnd.heetch;ver=2'
        }
        
        if self.okta_auth:
            headers['Heetch-Operator-Okta-Id'] = env.okta_user
        
        return headers
    
    def get_origin(self):
        return '{}-{}'.format(env.app_name, self.process)

    def run(self):
        return

    def isNaN(self, num):
        return num != num
    
    # Check column name & type
    def validate_dataset(self):
        for req in self._df_cols:
            if req['col'] not in self.df.columns:
                raise TypeError('Dataset definition error : {} column is not defined'.format(req['col']))

            # For boolean type, try to cast if input is str
            if req['type'] is 'bool' and type(self.df[req['col']]).__name__ is 'str':
                dict = {'false': False, 'true': True}
                self.df[req['col']] = self.df[req['col']].str.lower().map(dict)

                # NaN Value will be present if it could not replace false/true value
                if self.df[req['col']].isnull().values.any():
                    raise TypeError(
                        'Dataset definition error : {} column is not of type {}'.format(req['col'], req['type']))

            # disabled for now because integer can be str (ei : id as url param)
            # if req['type'] is not 'bool' and type(self.df[req['col']]).__name__ is not req['type']:
            # raise TypeError('Dataset definition error : {} column is not of type {}'.format(req['col'], req['type']))

    def post_data(self):
        errors_df = pd.DataFrame(data=None, columns=self.df.columns)
        errors_df['error'] = ''
        errors_list = []
        for index, row in self.df.iterrows():
            try:
                r = self.post_request(row)
                r.raise_for_status()
                print('POST status = {}'.format(r.status_code))
            except requests.exceptions.RequestException as e:
                print('[Error]', e)
                row['error'] = e
                errors_list.append(row)

        errors_df = pd.DataFrame(errors_list)
        errors_dataset_name = self.create_errors_dataset(errors_df)

        if not errors_df.empty:
            raise Exception('Errors occured when importing data ... . Check dataset {} to get more detail'.format(
                errors_dataset_name))

    # This method creates DSS dataset object and write the errors in it
    # The dataset is S3Connection stored in either 'dataiku-s3-test' or 'dataiku-s3-prod' based on the node type
    def create_errors_dataset(self, errors_df, df_name=None):
        if df_name is None:
            df_name = self.df_name
        client = dataiku.api_client()
        project = client.get_project(dataiku.default_project_key())
        project_variables = dataiku.get_custom_variables()
        errors_dataset_name = '{}_import_errors'.format(df_name)

        # Create dataset if it doesn't already exist
        try:
            # If dataset exists, clear it
            errors_dataset = project.get_dataset(errors_dataset_name)  # doesn't generate error if dataset doesn't exist
            errors_dataset.clear()
        except:
            # Create dataset (assuming exception was that dataset does not exist)
            params = {'connection': env.s3_connection,
                      'path': '/managed/' + project_variables['projectKey'] + '/' + errors_dataset_name}
            format_params = {'separator': '\t', 'style': 'excel', 'compress': ''}

            errors_dataset = project.create_dataset(errors_dataset_name, type='S3', params=params,
                                                    formatType='csv', formatParams=format_params)

            ds_def = errors_dataset.get_definition()
            ds_def['managed'] = True
            errors_dataset.set_definition(ds_def)

        # Set dataset to managed
        errors_dataset = dataiku.Dataset(errors_dataset_name)  # use this module to write
        errors_dataset.write_with_schema(errors_df)

        return errors_dataset_name
