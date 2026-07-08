#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import sqlite3
import mysql.connector

from infrastructure.runtime_paths import local_database_path


class CreateDatabase:
    def __init__(self, host="", database="", user="", password="", is_local: bool = False):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.is_local = is_local
        self.db_path = local_database_path(self.database) if self.is_local else None
        self.initialize_database()

    def connect(self):
        """Establece conexión con una base de datos MySQL específica."""
        if self.is_local:
            # --- CONEXIÓN LOCAL SQLITE ---
            return sqlite3.connect(self.db_path)
        else:
            return mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=True,
                use_pure=True
            )

    def initialize_database(self):
        if self.is_local:
            # --- FLUJO SQLITE ---
            # Al conectar, SQLite crea el archivo automáticamente. No hace falta "CREATE DATABASE"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            self._create_sqlite_tables(cursor)
            self._migrate_sqlite_budget_lines(cursor)
            conn.commit()
            conn.close()
            print(f"¡Base de datos local SQLite [{self.database}] configurada con éxito!")
        else:
            conn_server = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                autocommit=True,
                use_pure=True
            )
            cursor_server = conn_server.cursor()
            cursor_server.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor_server.close()
            conn_server.close()

            # Paso 2: Ahora que la DB existe, nos conectamos a ella para crear las tablas
            conn = self.connect()
            cursor = conn.cursor()

            self._create_mysql_tables(cursor)
            self._migrate_mysql_budget_lines(cursor)
            cursor.close()
            conn.close()
            print(f"¡Base de datos remota MySQL [{self.database}] configurada con éxito!")

    def _create_sqlite_tables(self, cursor):
        """Crea las tablas usando el dialecto de SQLite."""

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS company_profile
                       (
                           id      INTEGER PRIMARY KEY CHECK (id = 1), -- Forzamos a que solo exista la fila 1
                           name    TEXT NOT NULL,
                           cif     TEXT NOT NULL,
                           address TEXT,
                           email   TEXT,
                           phone   TEXT
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           product_id  TEXT PRIMARY KEY,
                           name        TEXT NOT NULL,
                           description TEXT,
                           base_price  REAL NOT NULL,
                           category    TEXT
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS budgets
                       (
                           id          INTEGER PRIMARY KEY AUTOINCREMENT,
                           nif_cif     TEXT,
                           client_name TEXT NOT NULL,
                           budget_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                           total       REAL NOT NULL
                       )
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS budget_lines
                       (
                           id         INTEGER PRIMARY KEY AUTOINCREMENT,
                           budget_id  INTEGER,
                           description TEXT,
                           concept    TEXT,
                           product    TEXT,
                           product_id TEXT,
                           unit       TEXT,
                           quantity   REAL,
                           unit_price REAL,
                           price      REAL,
                           discount_pct REAL DEFAULT 0,
                           tax_pct    REAL DEFAULT 21,
                           notes      TEXT,
                           FOREIGN KEY (budget_id) REFERENCES budgets (id),
                           FOREIGN KEY (product_id) REFERENCES products (product_id)
                       )
                       ''')

    def _create_mysql_tables(self, cursor):
        """Crea las tablas usando el dialecto adaptado para MySQL."""
        # En MySQL, las claves primarias de texto deben ser VARCHAR

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS company_profile
                       (
                           id      INT PRIMARY KEY DEFAULT 1,
                           name    VARCHAR(255) NOT NULL,
                           cif     VARCHAR(50)  NOT NULL,
                           address TEXT,
                           email   VARCHAR(100),
                           phone   VARCHAR(50),
                           CONSTRAINT chk_single_row CHECK (id = 1) -- MySQL moderno soporta CHECK constraints
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           product_id  VARCHAR(50) PRIMARY KEY,
                           name        VARCHAR(255)   NOT NULL,
                           description TEXT,
                           base_price  DECIMAL(10, 2) NOT NULL,
                           category    VARCHAR(100)
                       )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                       ''')

        # Cambiamos INTEGER por INT y AUTOINCREMENT por AUTO_INCREMENT
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS budgets
                       (
                           id          INT AUTO_INCREMENT PRIMARY KEY,
                           nif_cif     VARCHAR(50),
                           client_name VARCHAR(255)   NOT NULL,
                           budget_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                           total       DECIMAL(10, 2) NOT NULL
                       )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                       ''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS budget_lines
                       (
                           id         INT AUTO_INCREMENT PRIMARY KEY,
                           budget_id  INT,
                           description TEXT,
                           concept    VARCHAR(255),
                           product    VARCHAR(255),
                           product_id VARCHAR(50),
                           unit       VARCHAR(50),
                           quantity   DECIMAL(10, 3),
                           unit_price DECIMAL(10, 2),
                           price      DECIMAL(10, 2),
                           discount_pct DECIMAL(10, 2) DEFAULT 0,
                           tax_pct    DECIMAL(10, 2) DEFAULT 21,
                           notes      TEXT,
                           FOREIGN KEY (budget_id) REFERENCES budgets (id) ON DELETE CASCADE,
                           FOREIGN KEY (product_id) REFERENCES products (product_id)
                       )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                       ''')

    def _migrate_sqlite_budget_lines(self, cursor):
        cursor.execute("PRAGMA table_info(budget_lines)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        columns_to_add = [
            ("description", "TEXT"),
            ("product", "TEXT"),
            ("unit", "TEXT"),
            ("unit_price", "REAL"),
            ("discount_pct", "REAL DEFAULT 0"),
            ("tax_pct", "REAL DEFAULT 21"),
            ("notes", "TEXT"),
        ]

        for column_name, column_sql in columns_to_add:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE budget_lines ADD COLUMN {column_name} {column_sql}")

    def _migrate_mysql_budget_lines(self, cursor):
        columns_to_add = [
            ("description", "TEXT"),
            ("product", "VARCHAR(255)"),
            ("unit", "VARCHAR(50)"),
            ("unit_price", "DECIMAL(10, 2)"),
            ("discount_pct", "DECIMAL(10, 2) DEFAULT 0"),
            ("tax_pct", "DECIMAL(10, 2) DEFAULT 21"),
            ("notes", "TEXT"),
        ]

        for column_name, column_sql in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE budget_lines ADD COLUMN IF NOT EXISTS {column_name} {column_sql}")
            except Exception:
                # Si el motor no soporta IF NOT EXISTS o la columna ya existe, seguimos.
                pass
