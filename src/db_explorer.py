"""
db_explorer.py
Izveido savienojumu ar MySQL serveri un izgūst shēmas informāciju.
"""

import mysql.connector
from dataclasses import dataclass, field


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    full_type: str
    nullable: bool
    constraints: list = field(default_factory=list)
    default: str = None
    comment: str = ""


@dataclass
class TableInfo:
    name: str
    columns: list = field(default_factory=list)
    comment: str = ""
    row_count: int = None


def connect(host, port, user, password, database):
    return mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        connect_timeout=10,
    )


def get_tables(cursor, database):
    cursor.execute(
        """
        SELECT TABLE_NAME, TABLE_COMMENT, TABLE_ROWS
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """,
        (database,),
    )
    tables = []
    for row in cursor.fetchall():
        tables.append(TableInfo(name=row[0], comment=row[1] or "", row_count=row[2]))
    return tables


def get_columns(cursor, database, table_name):
    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE,
               IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """,
        (database, table_name),
    )
    columns = []
    for row in cursor.fetchall():
        name, data_type, full_type, nullable, key, default, extra, comment = row
        constraints = []
        if key == "PRI":
            constraints.append("PRIMARY KEY")
        if key == "UNI":
            constraints.append("UNIQUE")
        if key == "MUL":
            constraints.append("INDEXED")
        if nullable == "NO":
            constraints.append("NOT NULL")
        if extra == "auto_increment":
            constraints.append("AUTO_INCREMENT")
        columns.append(
            ColumnInfo(
                name=name,
                data_type=data_type,
                full_type=full_type,
                nullable=(nullable == "YES"),
                constraints=constraints,
                default=default,
                comment=comment or "",
            )
        )
    return columns


def get_foreign_keys(cursor, database, table_name):
    cursor.execute(
        """
        SELECT kcu.COLUMN_NAME, kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
        WHERE kcu.TABLE_SCHEMA = %s AND kcu.TABLE_NAME = %s
          AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
        """,
        (database, table_name),
    )
    return [
        {"column": r[0], "references_table": r[1], "references_column": r[2]}
        for r in cursor.fetchall()
    ]


def explore_database(connection, database):
    cursor = connection.cursor()
    tables = get_tables(cursor, database)
    for table in tables:
        table.columns = get_columns(cursor, database, table.name)
        fk_map = {fk["column"]: fk for fk in get_foreign_keys(cursor, database, table.name)}
        for col in table.columns:
            if col.name in fk_map:
                fk = fk_map[col.name]
                col.constraints.append(f"FK -> {fk['references_table']}.{fk['references_column']}")
    cursor.close()
    return tables
