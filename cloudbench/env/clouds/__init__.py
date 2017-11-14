from .azure import AzureCloud
from .aws import AwsCloud
from .gcloud import GcloudCloud
from .local import LocalCloud
from .openstack import OpenstackCloud

__all__ = ['AzureCloud', 'AwsCloud', 'GcloudCloud', "LocalCloud", "OpenstackCloud"]
