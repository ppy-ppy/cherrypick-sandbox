# from .azure_storage import AzureStorage
from .file_storage import FileStorage
from .json_storage import JsonStorage

__all__ = ['FileStorage', 'JsonStorage']
