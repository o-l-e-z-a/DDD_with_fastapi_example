from src.infrastructure.other_service_integration.client_interface import Client


class ServiceNotAvailableError(Exception):
    pass


class BaseServiceIntegration:
    def __init__(self, client: Client, base_url: str):
        self.client = client
        self.base_url = base_url
