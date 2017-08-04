# from IxnHttp import IxnHttp
from ixnetwork.IxnFileManagement import IxnFileManagement
import json


class IxnConfigManagement(object):
    """Configuration management """
    
    def __init__(self, ixnhttp):
        self._ixnhttp = ixnhttp
        self._file_mgmt = IxnFileManagement(ixnhttp)
    
    def new_config(self):
        """Create an empty configuration"""
        self._ixnhttp.root.operations.newconfig()

    def load_config(self, filename, upload=False, remove_chassis=False):
        """Load a binary .ixncfg configuration into the test tool """
        filename_only = self._file_mgmt._get_filename(filename)
        if upload:
            self._file_mgmt.upload(filename)
        if len(self._file_mgmt.files(match=filename_only)) == 0:
            raise Exception('file not found on server')
        self._ixnhttp.root.operations.loadconfig({'arg1': filename_only})
        if remove_chassis is True:
            query_result = ixnhttp.root.query \
                .node('availableHardware') \
                .node('chassis') \
                .go()
            for chassis in query_result.availableHardware.chassis:
                chassis.delete()
            

    def save_config(self, remote_filename, download=False, local_filename=None):
        """Save the test tool configuration as a binary .ixncfg """
        self.file_mgmt.create(remote_filename)
        self._ixnhttp.root.operations.saveconfig({'arg1': remote_filename})
        if download:
            if local_filename is None:
                local_filename = remote_filename
            self.file_mgmt.download(remote_filename, local_filename)

    def export_config(self, start_xpath='/', descend=True, include_defaults=True, local_filename=None, export_format='json'):
        """Export the test tool's current configuration 
        
        :param start_xpath: The xpath at which the export will start at 
        :param descend: True to recursively export child objects, False to export only the start_xpath object 
        :param include_defaults: True to export properties whose values are the same as default values, False to exclude them
        :param local_filename: Write the exported json to a file instead of returning a string
        :param export_format: Export the configuration in one of the following formats (json)
        :returns: JSON configuration as a string if the local_filename is not specified
        """
        payload = {
            'arg1': start_xpath, 
            'arg2': descend, 
            'arg3': include_defaults,
            'arg4': export_format
        }
        if local_filename is not None:
            self._file_mgmt.create(local_filename)
            filename_only = self._file_mgmt._get_filename(local_filename)
            payload['arg5'] = filename_only
        response = self._ixnhttp.root.operations.exportconfig(payload)
        if local_filename is not None:
            self._file_mgmt.download(filename_only, local_filename)
        else:
            return json.loads(response.result)

    def import_config(self, config):
        """Replace the test tool configuration with a JSON configuration """
        json_string = json.dumps(config)
        return self._ixnhttp.root.operations.importconfig({'arg1': json_string, 'arg2': True})

    def configure(self, config):
        """Modify the test tool configuration with a JSON configuration """
        json_string = json.dumps(config)
        return self._ixnhttp.root.operations.importconfig({'arg1': json_string, 'arg2': False})
