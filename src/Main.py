from Downloader import Downloader
from DigitClassifier import DigitClassifier
import numpy as np
from TheBlueAllianceAPI import get_event_match_keys_with_vidoes, get_event_match_outcomes
from MatchProcessing import MatchProcessing
from DataBaseWorker import DataBaseWorker
from MatchProcessingWorker import MatchProcessingWorker
import time


score_classifier = DigitClassifier('C:\\Users\\darkd\\Documents\\ScoreProject\\knntrain\\', (15, 20), np.array([200,200,200]), np.array([255, 255, 255]))
time_classifier = DigitClassifier('C:\\Users\\darkd\\Documents\\ScoreProject\\knntraintime\\', (14, 20), np.array([0,0,0]), np.array([120, 120, 120]))


d = Downloader('https://www.youtube.com/watch?v=hbLME8QLdeU', 'C:\\Users\\darkd\\Documents\\ScoreProject\\', 'testmilian')
d.download()
match = MatchProcessing(d.name, score_classifier, time_classifier)

states = match.process_match()

print(states)


# db = DataBaseWorker('C:\\Users\\darkd\\Documents\\ScoreProject\\timeseriesdb.db')
# db.start()
# event_name = ['2018mibel', '2018milan', '2018miwmi', '2018miesc', '2018migay', '2018migul', '2018milin', '2018mimid']
# thread_list = []
# for event in event_name:
#     matches_and_vidoes = get_event_match_keys_with_vidoes(event)
#     for key, value in matches_and_vidoes.items():
#         try:
#             d = Downloader('https://www.youtube.com/watch?v=%s' % value[0],
#                            'C:\\Users\\darkd\\Documents\\ScoreProject\\', key)
#             d.download()
#             worker = MatchProcessingWorker(d.name, db, event, value[1], key, score_classifier, time_classifier)
#             thread_list.append(worker.start())
#         except Exception as e:
#             print("ERROR in Main thread: %s : %s" % (key, str(e)))
#     print('Done with Matches %s' % event)
#
# for worker_thread in thread_list:
#     worker_thread.join()
#
# time.sleep(1)
# db.stop()




# event_name = ['2018miket','2018misou', '2018mitvc', '2018mike2', '2018misjo', '2018miwat', '2018micen', '2018mimil']
# for event in event_name:
#     matches_and_vidoes = get_event_match_outcomes(event)
#     for key, value in matches_and_vidoes.items():
#         print("%s, %s" % (key, value))