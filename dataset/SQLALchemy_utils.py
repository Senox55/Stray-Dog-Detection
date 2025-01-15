from typing import Any

from sqlalchemy import MetaData, inspect, create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeMeta, declarative_base


class PostgresConnection:
    def __init__(self,
                 host: str = "localhost",
                 port: int | str = 5432,
                 user: str | None = None,
                 password: str | None = None):

        database_url = f'postgresql://{user}:{password}@{host}:{port}'

        self.__engine = create_engine(database_url)

        self.session = Session(bind=self.__engine)

    def create_tables(self, Base):
        Base.metadata.create_all(bind=self.__engine)

    def get_data_from_table(self, table_class=None, table_name: str = None, columns: list[str] | None = None) -> list:
        """
        Get data from specific columns in a table.
        Args:
            table_class: ORM class representing the table.
            table_name (str): Name of the table to insert data into.
            columns (list[str]): List of column names to fetch. If not provided -> all table columns
        Returns:
            list[dict]: List of rows with specified columns.
        """

        if table_class:
            table_obj = table_class.__table__

        elif table_name:
            metadata = MetaData()
            metadata.reflect(bind=self.session.bind)
            table_obj = metadata.tables.get(table_name)
            if table_obj is None:
                raise ValueError(f"Table '{table_name}' does not exist.")

        else:
            raise ValueError("Either table_class or table_name must be provided.")

        inspector = inspect(table_obj)
        if columns is None:
            columns = [column.name for column in inspector.columns]
        else:
            columns = [column.name for column in inspector.columns]
            invalid_columns = [col for col in columns if col not in columns]
            if invalid_columns:
                raise ValueError(f"Invalid columns {invalid_columns} for table {table_obj.name}")

        # Query the database
        query = self.session.query(*[column for column in inspector.columns if column.name in columns])
        results = query.all()

        return results

    def insert_data_to_table(self,
                             data: list[list[str]],
                             columns: list[str] | None = None,
                             table_class=None,
                             table_name: str = None) -> list:
        """
        Insert data into a specific table using ORM classes or a table name.
        Args:
            data (list(list(str))): A list of rows with data.
            columns: (list(str)) | None: A list of column names. If None then all table columns.
            table_class: ORM class representing the table.
            table_name (str): Name of the table to insert data into.
        """

        if table_class:
            table_obj = table_class.__table__

        elif table_name:
            metadata = MetaData()
            metadata.reflect(bind=self.session.bind)
            table_obj = metadata.tables.get(table_name)
            if table_obj is None:
                raise ValueError(f"Table '{table_name}' does not exist.")

        else:
            raise ValueError("Either table_class or table_name must be provided.")

        inspector = inspect(table_obj)

        if columns is None:
            columns = [column.name for column in inspector.columns]

        table_columns = [column.name for column in inspector.columns]
        invalid_columns = [col for col in columns if col not in table_columns]
        if invalid_columns:
            raise ValueError(f"Invalid columns {invalid_columns} for table {table_obj.name}")

        inserted_primary_keys = []
        for row in data:
            insert_data = {key: value for key, value in zip(columns, row)}
            result = self.session.execute(table_obj.insert().values(**insert_data))

            inserted_primary_keys.extend(result.inserted_primary_key)

        self.session.commit()

        return inserted_primary_keys

    def get_tables_list(self) -> list[str]:
        """
        List all tables in the database.
        Returns:
            list[str]: List of table names.
        """

        inspector = inspect(self.session.bind)
        return inspector.get_table_names()

    def get_columns_list(self, table_name: str = None, table_class=None) -> list[str]:
        """
        List all columns in a specific table.
        Args:
            table_name (str): Name of the table to inspect.
            table_class: ORM class representing the table.
        Returns:
            list[str]: List of column names.
        """

        if table_name is None:
            if table_class is None:
                ValueError(f"Table name or table class must be provided")
            else:
                table_name = table_class.__tablename__

        inspector = inspect(self.session.bind)
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Table '{table_name}' does not exist.")

        return [column['name'] for column in inspector.get_columns(table_name)]

    def delete_tables(self, table_names: list[str] = None, table_classes: list = None) -> None:
        """
        Delete tables from the database. Table names and table classes will be united
        Args:
            table_classes list: List of ORM classes that represent table.
            table_names list(str): List of names of the tables to drop.
        """
        if table_names is None:
            table_names = []
        if table_classes is None:
            table_classes = []

        table_names_from_classes = [t_class.__tablename__ for t_class in table_classes]
        if table_names_from_classes:
            table_names.extend(table_names_from_classes)
            table_names = set(table_names)

        if not table_names:
            ValueError(f"Table names or table classes must be provided")

        for table_name in table_names:
            metadata = MetaData()
            metadata.reflect(bind=self.session.bind)
            table_obj = metadata.tables.get(table_name)

            if table_obj is None:
                raise ValueError(f"Table '{table_name}' does not exist.")

            table_obj.drop(self.session.bind)
