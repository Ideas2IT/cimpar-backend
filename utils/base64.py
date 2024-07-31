import base64
import re
from azure.storage.blob import BlobServiceClient

class HL7Processor:
    @staticmethod
    def extract_base64_from_hl7_message(hl7_message, identifier="SOFTGIS^IM^PDF^Base64"):
        """
        Extract the base64 encoded string from an HL7 message based on a given identifier.

        Args:
            hl7_message (str): The HL7 message as a string.
            identifier (str): The identifier to look for in the HL7 message.

        Returns:
            str: The extracted base64 encoded string, or None if not found.
        """
        base64_pattern = re.compile(rf"{re.escape(identifier)}\^(.+)")
        for line in hl7_message.splitlines():
            match = base64_pattern.search(line)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def save_base64_to_pdf(base64_str, output_path):
        """
        Save a base64 encoded string as a PDF file.

        Args:
            base64_str (str): The base64 encoded string.
            output_path (str): The path where the PDF should be saved.
        """
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(base64.b64decode(base64_str))

    @staticmethod
    def upload_to_azure_blob(container_name, blob_name, file_path, connection_string):
        """
        Upload a file to Azure Blob Storage.

        Args:
            container_name (str): The name of the container.
            blob_name (str): The name of the blob.
            file_path (str): The path of the file to upload.
            connection_string (str): The connection string to the Azure Storage account.
        """
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"File {file_path} uploaded to {container_name}/{blob_name}.")


