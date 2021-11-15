from .. import env
import requests
import dataiku
import pandas as pd
from action_interface import ActionInterface

##################################### Action Interface ####################################
class ImportCsvInterface(ActionInterface):

    def __init__(self,
                 df_name,
                 df,
                 token,
                 process):
        # because it s python 2.7
        ActionInterface.__init__(self,
                                 df_name,
                                 df,
                                 token)
        self._process = process
        
    
    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, process):
        self._process = process