import dataikuapi
import os

host = os.getenv('DSS_AUTOMATION_HOST', default=None)
api_key = os.getenv('DSS_AUTOMATION_API_KEY', default=None)
git_remote = 'git@github.com:heetch/dss-plugin-heetch-admin.git'
git_revision = os.getenv('GIT_REVISION', default=None)

if host is None or api_key is None or git_revision is None:
    print('host, api_key, git_revision is needed')
    exit(1)

try:
    design_client = dataikuapi.DSSClient(host, api_key)
    plugin = design_client.get_plugin("heetch-admin")
    # test if plugin exists ...
    settings = plugin.get_settings()
    plugin.update_from_git(git_remote, git_revision)
except Exception as e:
    print(e)
