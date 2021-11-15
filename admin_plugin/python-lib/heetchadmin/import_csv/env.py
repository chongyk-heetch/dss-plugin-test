import ConfigParser
import dataiku

configParser = ConfigParser.ConfigParser()
data_dir_path = dataiku.get_custom_variables().get('dip.home')
configParser.read(data_dir_path + "/install.ini")
current_node = configParser.get('general', 'nodetype')
api_url = 'https://dss-gw--stable.clusters.kalyke.heetch.net'
s3_connection = 'dataiku-s3-test'
app_name = 'dss-design'
okta_user = 'f8bd2822-002a-478f-66a9-0178efd7ee1f'

if current_node == 'automation':
    api_url = 'https://dss-gw.heetch.com'
    s3_connection = 'dataiku-s3-prod'
    app_name = 'dss-automation'

users_comments_endpoint = '/v2/users/{0}/comments'
ride_comments_endpoint = '/internal-activity/v1/ride-order-comments'
driver_suspension_endpoint = '/admin/drivers/{0}/suspend'
passenger_suspension_endpoint = '/v1/passengers/suspend'
driver_unsuspension_endpoint = '/admin/drivers/{0}/unsuspend'
passenger_unsuspension_endpoint = '/v1/passengers/unsuspend'
driver_document_request_endpoint = '/requests'
product_lines_assignment_endpoint = '/drivers/{0}/product_lines/{1}/assignment'
passenger_fraudster_endpoint = '/users/{0}/fraudster'
campaign_passenger_endpoint = '/campaigns/{0}/passengers'
canvas_add_endpoint = '/canvases'
canvas_update_endpoint = '/canvases/{0}'
canvas_passenger_endpoint = '/canvases/{0}/passengers'


import_csv_config_template = [
    'action',
    'dataset',
    'token',
    'process'
]

product_line_config_template = [
    'action',
    'dataset',
    'token'
]

campaign_passenger_config_template = [
    'action',
    'dataset',
    'token'
]
