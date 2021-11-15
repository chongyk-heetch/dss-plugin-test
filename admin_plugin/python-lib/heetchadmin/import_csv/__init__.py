from actions.driver_document_request_action import DriverDocumentRequestAction
from actions.ops_comments_action import OpsCommentsAction
from actions.ride_comments_action import RideCommentsAction
from actions.passenger_unsuspention_action import PassengerUnsuspentionAction
from actions.passenger_suspention_action import PassengerSuspentionAction
from actions.driver_suspention_action import DriverSuspentionAction
from actions.driver_unsuspention_action import DriverUnsuspentionAction
from actions.product_lines_assign import ProdcutLinesAssignAction
from actions.product_lines_unassign import ProdcutLinesUnassignAction
from actions.passenger_fraudster_action import PassengerFraudsterAction
from actions.campaign_passenger_action import CampaignPassengerAction
from actions.canvas_add_action import CanvasAddAction
from actions.canvas_update_action import CanvasUpdateAction
from actions.canvas_passenger_action import CanvasPassengerAction
from actions.canvas_passenger_delete_action import CanvasPassengerDeleteAction
import env
import dataiku

def validate_keys(config, config_template):
    for key in config_template:
        if key not in config:
            raise TypeError('{} is not defined'.format(key))

def get_action(df_name,
               df,
               action,
               token,
               process):
    if action == 'ops_comment':
        return OpsCommentsAction(df_name, df, token, process)
    elif action == 'rides_comment':
        return RideCommentsAction(df_name, df, token, process)
    elif action == 'driver_suspension':
        return DriverSuspentionAction(df_name, df, token, process)
    elif action == 'passenger_suspension':
        return PassengerSuspentionAction(df_name, df, token, process)
    elif action == 'driver_unsuspension':
        return DriverUnsuspentionAction(df_name, df, token, process)
    elif action == 'passenger_unsuspension':
        return PassengerUnsuspentionAction(df_name, df, token, process)
    elif action == 'driver_document_request':
        return DriverDocumentRequestAction(df_name, df, token, process)
    elif action == 'product_lines_assign':
        return ProdcutLinesAssignAction(df_name, df, token, process)
    elif action == 'product_lines_unassign':
        return ProdcutLinesUnassignAction(df_name, df, token, process)
    elif action == 'passenger_fraudster':
        return PassengerFraudsterAction(df_name, df, token, process)
    
def get_action_product_line(df_name,
               df,
               action,
               token):
    if action == 'product_lines_assign':
        return ProdcutLinesAssignAction(df_name, df, token)
    elif action == 'product_lines_unassign':
        return ProdcutLinesUnassignAction(df_name, df, token)
    
def get_action_crm(df_name,
               df,
               action,
               token):
    if action == 'campaign_passenger':
        return CampaignPassengerAction(df_name, df, token)
    elif action == 'canvas_add':
        return CanvasAddAction(df_name, df, token)
    elif action == 'canvas_update':
        return CanvasUpdateAction(df_name, df, token)
    elif action == 'canvas_passenger':
        return CanvasPassengerAction(df_name, df, token)
    elif action == 'canvas_passenger_delete':
        return CanvasPassengerDeleteAction(df_name, df, token)


def get_df(step_config):
    ds = dataiku.Dataset(step_config['dataset'])

    config = ds.get_config()

    if 'partitions' in step_config and step_config['partitions'] and 'filePathPattern' in config['partitioning']:
        ds.add_read_partitions(step_config['partitions'])

    try :
        dataset_df = ds.get_dataframe()
    except Exception as err:
        if step_config['ignore_missing_partitions']:
            print("Missing partition: {0}".format(err))
            exit(0)
        
        raise Exception(err)
    
    return dataset_df