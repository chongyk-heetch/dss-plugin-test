# This file is the code for the plugin Python step step-export-dataset

import os, json, requests
from dataiku.customstep import *
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from heetchadmin.import_csv import get_action_crm, validate_keys, env, get_df

# the plugin's resource folder path (string)
resource_folder = get_step_resource()

# settings at the plugin level (set by plugin administrators in the Plugins section)
plugin_config = get_plugin_config()

# settings at the step instance level (set by the user creating a scenario step)
step_config = get_step_config()

validate_keys(step_config, env.product_line_config_template)

# Read recipe inputs
dataset_df = get_df(step_config)

action = get_action_crm(df_name=step_config['dataset'],
                               df=dataset_df,
                               action=step_config['action'],
                               token=step_config['token'])

action.run()
