import sqlite3
import queue
import threading
import time

class DataBaseWorker:
    def __init__(self, database_path):
        self.database_path = database_path
        # self.cursor = self.sql_connection.cursor()
        self.queue = queue.Queue()
        self.work = True

    def start(self):
        thread = threading.Thread(target=self._do_work)
        thread.start()

    def _do_work(self):
        print('Started DataBase')
        sql_connection = sqlite3.connect(self.database_path)
        cursor = sql_connection.cursor()
        while self.work:
            if not self.queue.empty():
                data = self.queue.get()
                for match_state in data[3]:
                    try:
                        cursor.execute("INSERT INTO match_table VALUES ('" + data[1] + "', '" + data[0] + "', '" + data[2] + "', ?, ?, ?, ?, ?, ?)", match_state.get_sql_format())
                    except:
                        print('Error with Adding row in SQL')

                sql_connection.commit()
            else:
                time.sleep(.1)
                # Sleep
        cursor.close()
        sql_connection.close()


    def add_to_queue(self, data):
        self.queue.put(data)

    def stop(self):
        self.work = False