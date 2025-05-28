import psycopg2
import argparse

# Function to connect to the PostgreSQL database
def connect_to_db(db_name, user, password, host='localhost', port='5432'):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# Function to retrieve the list of tables
def get_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    tables = cursor.fetchall()
    return [table[0] for table in tables]

# Function to retrieve information from columns in a table
def get_table_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable, character_maximum_length, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
    """)
    columns = cursor.fetchall()
    return columns

# Function to generate the .cpy file for a table
def generate_cpy_file(table_name, columns):
    cpy_content = f"""      *> -------------------------------------------
      *> DECLARE TABLE for {table_name}
      *> -------------------------------------------
       EXEC SQL DECLARE {table_name} TABLE
       (\n"""

    cobol_host_variables = f"""      *> -------------------------------------------
      *> COBOL HOST VARIABLES FOR TABLE {table_name}
      *> -------------------------------------------
       01  DCL{table_name}.
"""

    cobol_indicator_variables = f"""      *> -------------------------------------------
      *> COBOL INDICATOR VARIABLES FOR TABLE {table_name}
      *> -------------------------------------------
       01  DCL{table_name}-NULL.
"""

    first_column = True
    for column in columns:
        col_name = column[0]
        col_type = column[1]
        not_null = "NOT NULL" if column[2] == 'NO' else ""
        char_max_length = column[3]
        numeric_precision = column[4]
        numeric_scale = column[5]

        # Determine the SQL data type with the appropriate length
        if "character varying" in col_type or "varchar" in col_type:
            col_type_with_length = f"varchar({char_max_length})"
        elif "character" in col_type or "char" in col_type:
            col_type_with_length = f"bpchar({char_max_length})"
        elif col_type == "integer":
            col_type_with_length = "int4"
        elif col_type == "smallint":
            col_type_with_length = "int2"
        elif col_type == "numeric":
            precision = numeric_precision if numeric_precision else 10
            scale = numeric_scale if numeric_scale else 0
            if scale == 0:
                col_type_with_length = f"numeric({precision})"
            else:
                col_type_with_length = f"numeric({precision},{scale})"
        else:
            col_type_with_length = col_type

        # Mapping SQL types to COBOL
        cobol_type = ""
        if col_type == "integer":
            cobol_type = "pic s9(09) comp-5."
        elif col_type == "smallint":
            cobol_type = "pic s9(04) comp-5."
        elif col_type == "bigint":
            cobol_type = "pic s9(18) comp-5."
        elif col_type == "real":
            cobol_type = "comp-1."
        elif col_type == "double precision":
            cobol_type = "comp-2."
        elif "CHAR" in col_type.upper() or "TEXT" in col_type.upper():
            size = char_max_length if char_max_length else 255
            cobol_type = f"pic x({size})."
        elif "DATE" in col_type.upper():
            cobol_type = "pic x(10)."
        elif "TIME" in col_type.upper():
            cobol_type = "pic x(8)."
        elif "TIMESTAMP" in col_type.upper():
            cobol_type = "pic x(29)."
        elif col_type == "numeric":
            precision = numeric_precision if numeric_precision else 10
            scale = numeric_scale if numeric_scale else 0
            if scale == 0:
                cobol_type = f"pic s9({precision}) comp-3."
            else:
                cobol_type = f"pic s9({precision})v9({scale}) comp-3."

        # Add the comma only if it is not the first column.
        if first_column:
            cpy_content += f"           {col_name:<20} {col_type_with_length:<20} {not_null}\n"
            first_column = False
        else:
            cpy_content += f"         , {col_name:<20} {col_type_with_length:<20} {not_null}\n"
        
        cobol_host_variables += f"           03 {table_name}-{col_name:<20} {cobol_type}\n"
        cobol_indicator_variables += f"           03 {table_name}-{col_name}-NULL pic s9(04) comp-5.\n"

    cpy_content += "       ) END-EXEC.\n"
    cpy_content += cobol_host_variables
    cpy_content += cobol_indicator_variables
    cpy_content += "      *>----- End of file\n"

    return cpy_content

# Main function
def main(db_name, user, password, host='localhost', port='5432'):
    conn = connect_to_db(db_name, user, password, host, port)
    if conn:
        tables = get_tables(conn)
        for table in tables:
            columns = get_table_columns(conn, table)
            cpy_content = generate_cpy_file(table, columns)
            with open(f"{table}.cpy", "w") as f:
                f.write(cpy_content)
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate COBOL declarations from PostgreSQL database tables.')
    parser.add_argument('-d', '--database', required=True, help='Database name')
    parser.add_argument('-u', '--user', required=True, help='Database user')
    parser.add_argument('-p', '--password', required=True, help='Database password')
    parser.add_argument('-H', '--host', default='localhost', help='Database host')
    parser.add_argument('-P', '--port', default='5432', help='Database port')

    args = parser.parse_args()

    main(args.database, args.user, args.password, args.host, args.port)
 
