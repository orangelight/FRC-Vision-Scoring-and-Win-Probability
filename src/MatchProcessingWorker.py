import threading
from MatchProcessing import MatchProcessing
import os
import time


class MatchProcessingWorker:
    def __init__(self, video_file, database_queue, event_key, comp_level, match_key, score_digit_classifier, time_digit_classifier):
        self.path = video_file
        self.match = MatchProcessing(self.path, score_digit_classifier, time_digit_classifier)
        self.db = database_queue
        self.event_key = event_key
        self.match_key = match_key
        self.comp_level = comp_level


    def start(self):
        main_thread = threading.Thread(target=self._do_work)
        main_thread.start()
        return main_thread

    def _do_work(self):
        try:
            start = time.time()
            states = self.match.process_match()
            end = time.time()
            print('Vision Processing took %0.2f secs' % (end-start))
            self.db.add_to_queue([self.match_key, self.event_key, self.comp_level, states])
            print("DONE: %s" % self.match_key)
            os.remove(self.path)
        except Exception as e:
            self.match.clean_up()
            print('ERROR: with %s, %s' % (self.match_key, str(e)))

