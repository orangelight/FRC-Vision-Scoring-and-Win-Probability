import cv2
import numpy as np
from Frame import Frame
from ScoreState import ScoreState
from Util import MissingTimeException

class MatchProcessing:
    def __init__(self, file_path, score_digit_classifier, time_digit_classifier, skip_frames=15):
        self.file_path = file_path
        self.score_digit_classifier = score_digit_classifier
        self.time_digit_classifier = time_digit_classifier
        self.template_red_score_pos = np.matrix([[491,  46], [639,  46], [491, 117], [639, 117]])
        self.template_blue_score_pos = np.matrix([[641, 46], [789, 46], [641, 117], [789, 117]])

        self.template_to_frame_transform = None
        self.match_video_capture = cv2.VideoCapture(self.file_path)
        self.skip_frames = skip_frames
        self.flipped = False

        self.score_state_list = []

    def process_match(self):
        self._loop_through_frames_with_function(self._try_to_set_transform_with_frame)
        if self.template_to_frame_transform is None: # Reached end of the file
            self.clean_up()
            raise Exception('ERROR: Skipped Whole Video, no score overlay!')
        self._loop_through_frames_with_function(self._add_state_from_frame)
        self.clean_up()
        return self._clean_states_list()

    def _add_score_state_to_list(self, state):
        if len(self.score_state_list):
            if state.time+1 == self.score_state_list[-1].time:
                self.score_state_list.append(state)
            elif state.time > self.score_state_list[-1].time:
                print("Warning missing Frame(s) from %s to %s " % (str(self.score_state_list[-1].time), str(state.time)))
                self.score_state_list.append(state)
            elif state.time > self.score_state_list[-1].time:
                raise Exception('Error: Trying to add time greater than last time, from %s to %s' % (
                str(self.score_state_list[-1].time), str(state.time)))

        else:
            self.score_state_list.append(state)

    def _clean_states_list(self):
        new_state_list = []

        for i in range(len(self.score_state_list)):
            if not i == 0:
                if not self.score_state_list[i].time == self.score_state_list[i-1].time:
                    new_state_list.append(self.score_state_list[i])
            else:
                new_state_list.append(self.score_state_list[i])
        return new_state_list

    def _loop_through_frames_with_function(self, frame_function):
        read_frame_success = True
        frame_count = 0
        while read_frame_success:
            read_frame_success, frame_image = self.match_video_capture.read()
            frame = Frame(frame_image, score_digit_classifier=self.score_digit_classifier,
                              time_digit_classifier=self.time_digit_classifier, flipped=self.flipped, template_to_frame_transform=self.template_to_frame_transform)
            if not read_frame_success:
                break

            if frame_count % self.skip_frames == 0:
                if not frame_function(frame):
                    break
            frame_count += 1

    def _try_to_set_transform_with_frame(self, frame):
        found_red_box, frame_red_box_points, flipped = frame.find_red_score_box()
        if found_red_box:
            self.flipped = flipped
            if self.flipped:
                self.template_to_frame_transform = cv2.estimateRigidTransform(self.template_blue_score_pos, frame_red_box_points, False)
            else:
                self.template_to_frame_transform = cv2.estimateRigidTransform(self.template_red_score_pos, frame_red_box_points, False)
            return False  # Stop loop
        return True

    def _add_state_from_frame(self, frame):
        if frame.check_for_score_box():
            try:
                self._add_score_state_to_list(frame.get_score_state())
            except Exception as e:
                print('ERROR: with state %s' % str(e))
            if frame.is_match_over() or frame.is_match_under_review():
                return False  # Stop loop
            return True
        return False

    def clean_up(self):
        self.match_video_capture.release()
