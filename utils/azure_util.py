from azure.storage.blob import BlobServiceClient


class AzureUtil:

    @staticmethod
    def upload_to_azure_blob(container_name, blob_name, blob_data, connection_string):
        """
        Upload a file to Azure Blob Storage.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob.
            blob_data ): The data to be uploaded
            connection_string (str): The connection string to the Azure Storage account.
        """
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # with open(file_path, "rb") as data:
        blob_client.upload_blob(blob_data, overwrite=True)
