from src.db import get_connection

def get_schema_text():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()] #extracting 1st col of each row

    schema = []
    for table in tables:
        #for primary key
        cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
        pk_row = cursor.fetchone()
        pk_col = pk_row[4] if pk_row else None

        #for foreign keys
        cursor.execute(f"""
                       SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                       FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                       WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL
                       """, (table,))
        fks = cursor.fetchall()
        fk_map = {fk[0]: (fk[1], fk[2]) for fk in fks}

        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        schema.append(f"Table: {table}")
        for col in cols:
            col_name = col[0]
            col_type = col[1]
            extra = []

            if col_name == pk_col:
                extra.append("Primary key")
            if col_name in fk_map:
                ref_table, ref_col = fk_map[col_name]
                extra.append(f"Foreign key to {ref_table}.{ref_col}")

            extras_str = f" - {',' .join(extra)}" if extra else ""

            schema.append(f" - {col_name} ({col_type}){extras_str}")
        schema.append("")

    conn.close()
    return "\n".join(schema) #returning as text block for LLm prompt

