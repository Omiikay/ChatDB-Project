'''
File name: mysqlApi
Function: infer_column_types, save_upload_mysql, show_table, mysql_send
Comment: Use to process data and message Mysql.
'''

from application import mysql
from application import constant
import pandas as pd


def infer_column_types(df: pd.DataFrame):
    """
    TODO: phrase dataframe
    """
    type_mapping = {
        'int64': 'INT',
        'float64': 'FLOAT',
        'object': 'VARCHAR(255)',
        'datetime64[ns]': 'DATETIME'
    }
    return {col: type_mapping[str(dtype)] for col, dtype in df.dtypes.items()}

def save_upload_mysql(inputFile, df: pd.DataFrame):
    # Loading or Opening the csv file
    
    if inputFile:
        file_name = inputFile.filename.split('.')[0]
        #print("successfully get " + file_name)
        file_type = inputFile.content_type
        if file_type == constant.TYPE_CSV:
            try:
                conn = mysql.connect
                cursor = conn.cursor()

                #prepare sql
                table_name = file_name
                column_types = infer_column_types(df)

                # CREATE TABLE 
                columns_definition = ", ".join([f"`{col}` {dtype}" for col, dtype in column_types.items()])
                create_table_sql = f"CREATE TABLE `{table_name}` ({columns_definition});"

                # check if exists
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")  # 避免冲突
                cursor.execute(create_table_sql)

                # INSERT INTO 
                placeholders = ", ".join(["%s"] * len(df.columns))
                insert_sql = f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in df.columns])}) VALUES ({placeholders})"

                # convert csv to dict records format by pandas
                cursor.executemany(insert_sql, df.to_records(index=False).tolist())
                conn.commit()
                print(f'File {file_name} upload successfully!')

            except Exception as e:
                print(e)

            finally:
                cursor.close()
                conn.close()

        else:
            print("Error file type!")

def show_tables(table):
    try:
        # connect Mysql
        conn = mysql.connect
        cursor = conn.cursor()

        # execute query
        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        result = list(cursor.fetchall())
        # get attributes
        fields = [desc[0] for desc in cursor.description]

        if result:
            return f"Attributes: {fields}" + f"\n\n\t" + ",\n\t".join(list(map(str, result)))
        else:
            return f"()" + "\n\n"

    except Exception as e:
        print("Error " + str(e))
        return "Invalid Query, please try again!\n"
    
    finally:
        # close 
        cursor.close()
        conn.close()


def mysql_send(format_sql: str):
    try:
        conn = mysql.connect
        cursor = conn.cursor()

        cursor.execute(format_sql)
        result = list(cursor.fetchall())
        fields = [desc[0] for desc in cursor.description]

        if result:
            return f"Result:\n\n" + \
                   f'SQL: {format_sql}\n\n' + \
                   f"Attributes: {fields}" + \
                   f"\n\n\t" + ",\n\t".join(list(map(str, result))) + \
                   f"\n\n"
        else:
            return f"Result:\n\n" + \
                   f'SQL: {format_sql}\n\n' + \
                   f"()" + \
                   f"\n\n"
                   
    except Exception as e:
        print("Error " + str(e))
        return "Invalid Query, please try again!\n\n\n"
    
    finally:
        cursor.close()
        conn.close()
