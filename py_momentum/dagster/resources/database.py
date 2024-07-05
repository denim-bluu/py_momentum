from dagster import ConfigurableResource
from sqlalchemy import create_engine


class DatabaseResource(ConfigurableResource):
    connection_string: str

    def get_engine(self):
        return create_engine(self.connection_string)
