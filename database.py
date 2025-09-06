import sqlite3
import os
import re

DATABASE="database/data/tgbot.db"

class Database:
    __connection: sqlite3.Connection
    __cursor: sqlite3.Cursor
    
    def __init__(self, name: str | None = None):
        self.__connection = sqlite3.connect(name if name is not None else DATABASE)
        self.__cursor = self.__connection.cursor()
        self.__bootstrap()
    
    def __bootstrap(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (id integer primary key, name text);
        """)
        
        self.__connection.commit()
        return

    def readone(self, query: str, params: list = []):
        return self.__cursor.execute(query, params).fetchone()
        
    def readmany(self, query: str):
        self.__cursor.execute(query)
        return self.__cursor.fetchall()
        
    def insertone(self, query: str, data: tuple):
        self.__cursor.execute(query, data)
        self.__connection.commit()
    
    def execute(self, query: str):
        self.__cursor.execute(query)
        self.__connection.commit()
    
    def executeMany(self, query: str):
        self.__cursor.executemany(query, [])
        self.__connection.commit()
        return True
    
    def _parse_sql(self, sql: str):
        lines = sql.splitlines(True)
        up = True
        parts = {
            'UP': '',
            'DOWN': ''
        }
        for l in lines:
            if l.strip() == "--- DOWN":
                up = False
                continue
            elif l.strip() == "--- UP":
                up = True
                continue

            if up is True:
                parts['UP'] = parts['UP'] + l
            else:
                parts['DOWN'] = parts['DOWN'] + l
        
        parts['UP'] = self._clean_sql_for_execution(parts["UP"])
        parts['DOWN'] = self._clean_sql_for_execution(parts["DOWN"])
        return parts
    
    def _get_up(self, sql: str):
        return self._parse_sql(sql)['UP']
    
    def _get_down(self, sql: str):
        return self._parse_sql(sql)['DOWN']

    def _clean_sql_for_execution(self, string: str):
        sql = string.split("---")[0]
        sql = sql.replace("\n", "")
        sql = re.sub(r"(\(|,)(\s{1,4}|\t)(\w+)", r"\1\3", sql)
        return sql
        
    def run_migrations(self):
        data = self.get_run_migrations()
        files = self.get_migration_files()
        files = [x for x in files if x not in data]
        
        for file in files: #[0:1]:
            with open(f"database/migrations/{file}", "r") as fh:
                content = fh.read()
                up = self._get_up(content)
                self.__cursor.executescript(up)
                self.__cursor.execute("INSERT INTO migrations (name) VALUES (?)", [file])
                self.__connection.commit()
                
                print(f"{file} - Done")
    
    def revert_migrations(self, count = 1):
        files = self.get_run_migrations()
        files = files[-1::-1][0:count]
        
        for file in files:
            with open(f"database/migrations/{file}", "r") as fh:
                content = fh.read()
                down = self._get_down(content)
                print(down)
                if down is not None:
                    self.__cursor.executescript(down)
                
                self.__cursor.execute("DELETE FROM migrations WHERE name=?", [file])
                self.__connection.commit()
                
                print(f"{file} - Reverted")
                
    def get_run_migrations(self):
        data = self.readmany("SELECT name FROM migrations")
        return [x[0] for x in data]

    def get_migration_files(self):
        migrations = []
        for _, _, filenames in os.walk("database/migrations"):
            for filename in filenames:
                if filename not in migrations:
                    migrations.append(filename)
        
        return sorted(migrations)
    
    def get_migrations(self):
        data = self.readmany("SELECT * FROM migrations")
        
        migrations = {}
        for _, name in data:
            migrations[name.strip()] = True
        
        for _, _, filenames in os.walk("database/migrations", ):
            print(filenames)
            for filename in filenames:
                if filename not in migrations:
                    migrations[filename.strip()] = False
                    
        print("-----------------------------")
        print("Name\t\t\t| Status |")
        print("-----------------------------")
        for m in migrations:
            print (m, end="\t| ")
            if migrations[m]:
                print("✅", end="\t |\n")
            else:
                print("❌", end="\t |\n")
            
        