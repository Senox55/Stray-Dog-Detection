import os

import psycopg2
from psycopg2 import sql


class PostgresConnection:
    def __init__(self,
                 host: str = "localhost",
                 port: int | str = 5432,
                 user: str | None = None,
                 password: str | None = None):
        mapping = (("host", host), ("port", port), ("user", user), ("password", password))
        conn_kwargs = {key: value for key, value in mapping if value is not None}

        self.conn = psycopg2.connect(**conn_kwargs)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        with open('sql_queries/create_tables.sql', 'r') as file:
            self.execute_sql_template(file.read())

    def delete_tables(self, table_names: list[str] | None = None):
        """
        Delete tables from the database.
        Args:
            table_names list(str): List of names of the tables to drop.
        """
        print(table_names, table_names is None)
        if table_names is None or len(table_names) == 0:
            raise ValueError(f"Table names must be provided")

        with open('sql_queries/delete_tables.sql', 'r') as file:
            sql_template = file.read()
            for table in table_names:
                self.execute_sql_template(sql_template, to_replace={"table": table})

    def get_tables_list(self) -> list[str]:
        """
        List all tables in the database.
        Returns:
            list[str]: List of table names.
        """
        with open('sql_queries/get_tables_list.sql', 'r') as file:
            result = self.execute_sql_template(file.read())

            if result is not None:
                return [x[0] for x in result]
            return []

    def get_columns_list(self, table_name: str) -> list[str]:
        """
        List all columns in a specific table.
        Args:
            table_name (str): Name of the table to inspect.
        Returns:
            list[str]: List of column names.
        """

        if table_name not in self.get_tables_list():
            raise ValueError(f"Table '{table_name}' does not exist.")

        with open('sql_queries/get_columns_list.sql', 'r') as file:
            result = self.execute_sql_template(file.read(), to_replace={'table': table_name})

            if result is not None:
                return [x[0] for x in result]
            return []

    def get_data_from_table(self, table_name: str, columns: list[str] | None = None) -> list:
        """
        Get data from specific columns in a table.
        Args:
            table_name (str): Name of the table to insert data into.
            columns (list[str]): List of column names to fetch. If not provided -> all table columns
        Returns:
            list[dict]: List of rows with specified columns.
        """

        if columns is None:
            columns = self.get_columns_list(table_name)

        with open('sql_queries/get_data_from_table.sql', 'r') as file:
            sql_template = file.read()

            return self.execute_sql_template(sql_template, to_replace={'table': table_name, 'columns': columns})

    def insert_data_to_table(self, table_name: str, data: list[list[str]], columns: list[str] | None = None):
        """
        Insert data into a specific table using a table name.
        Args:
            data (list(list(str))): A list of rows with data.
            columns: (list(str)) | None: A list of column names. If None then all table columns.
            table_name (str): Name of the table to insert data into.
        """

        if columns is None:
            columns = self.get_columns_list(table_name)

        with open('sql_queries/insert_data_to_table.sql', 'r') as file:
            sql_template = file.read()

            invalid_columns = [col for col in columns if col not in self.get_columns_list(table_name)]
            if invalid_columns:
                raise ValueError(f"Invalid columns {invalid_columns} for table {table_name}")

            for value in data:
                self.execute_sql_template(sql_template,
                                          to_replace={'table': table_name, "columns": columns, 'values': value},
                                          dont_commit=True)

            self.conn.commit()

    def execute_sql_template(self,
                             sql_query_base: str,
                             to_replace: dict[str, str | list] | None = None,
                             dont_commit=False) -> list[tuple] | None:
        """
        Execute SQL template with provided params.
        Args:
            sql_query_base (str): SQL template.
            to_replace (dict[str, str | list] | None): The data to replace SQL template with.
            dont_commit (bool): if True then won't commit changes to database.
        Returns:
            list[tuple] | None: DB data.
        """

        if to_replace is None:
            to_replace = {}

        # divide to_replace to identifiers and values for correct replacements
        identifiers = {}
        values = {}
        for key in to_replace:
            identifier_index = sql_query_base.find("{" + key + "}")
            value_index = sql_query_base.find("%" + key + "%")

            if identifier_index != -1 and value_index != -1:
                raise Exception(f"Repeated use of \"{key}\" key word")

            elif identifier_index != -1:
                if sql_query_base[identifier_index + 1:].find("{" + key + "}") != -1:
                    raise Exception(f"Repeated use of \"{key}\" key word")
                identifiers[key] = to_replace[key]

            elif value_index != -1:
                if sql_query_base[value_index + 1:].find("%" + key + "%") != -1:
                    raise Exception(f"Repeated use of \"{key}\" key word")
                values[key] = to_replace[key]

            else:
                raise Exception(f"\"{key}\" key word wasn't found is sql template")

        # print(f"Вводные данные \n {sql_query_base} \n identifiers {identifiers} \n values {values}")

        # INSERT IDENTIFIERS
        redacted_sql = self.__replace_identifiers_is_sql(sql_query_base, identifiers).as_string(self.cursor)

        # INSERT VALUES
        redacted_sql, args = self.__replace_values_in_sql(redacted_sql, values)

        try:
            self.cursor.execute(redacted_sql, args)
        except Exception as error:
            self.conn.rollback()
            raise error

        if not dont_commit:
            self.conn.commit()

        if self.cursor.description is not None:
            return self.cursor.fetchall()

    @staticmethod
    def __replace_identifiers_is_sql(sql_query_base: str, identifiers: dict[str, str | list]):
        # print("Замена идентификаторов")

        formating_dict = {}
        for key, value in identifiers.items():
            if isinstance(value, str):
                formating_dict[key] = sql.Identifier(value)
            if isinstance(value, list):
                formating_dict[key] = sql.SQL(', ').join(map(sql.Identifier, value))

        redacted_sql = sql.SQL(sql_query_base).format(**formating_dict)

        # print(redacted_sql)
        return redacted_sql

    @staticmethod
    def __replace_values_in_sql(sql_query_base: str, values: dict[str, str | list]):
        #  REPLACE CUSTOM ARGUMENTS
        args = []
        for key in values.keys():
            to_replace = "%" + key + "%"

            index = sql_query_base.find(to_replace)
            if index == -1:
                raise Exception("key_not_found")

            if isinstance(values[key], str):
                string_for_replacing = "%s"
            elif isinstance(values[key], list):
                string_for_replacing = "%s" + ", %s" * (len(values[key]) - 1)
            else:
                Exception("Argument is neither a list nor a string")

            args.append((index, values[key]))

            sql_query_base = sql_query_base[:index] + string_for_replacing + sql_query_base[index + len(to_replace):]

        #  PREPARE ARGUMENT FOR INSERTION
        args.sort(key=lambda x: x[0])

        new_args = []
        for arg_tuple in args:
            arg = arg_tuple[1]
            if isinstance(arg, str):
                new_args.append(arg)
            else:
                new_args.extend(arg)

        # print(f"Замена значений \n {sql_query_base} \n {new_args}")

        return sql_query_base, new_args


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    conn = PostgresConnection(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), user=os.getenv("DB_USER"),
                              password=os.getenv("DB_PASSWD"))
