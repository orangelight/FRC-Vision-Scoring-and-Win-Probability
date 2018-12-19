import cv2
import numpy as np
from Util import construct_bounding_box_array_from_contour, Side
from ScoreState import ScoreState
from Util import NoDigitContoursException
import random


class Frame:  # TODO Add exceptions
    def __init__(self, frame_image, template_to_frame_transform=None, score_digit_classifier=None,
                 time_digit_classifier=None, flipped=False):
        self.frame_image = frame_image
        self.template_to_frame_transform = template_to_frame_transform
        self.score_digit_classifier = score_digit_classifier
        self.time_digit_classifier = time_digit_classifier
        self.flipped = flipped

    def find_red_score_box(self):
        red_mask = cv2.inRange(self.frame_image, np.array([0, 0, 180]), np.array([75, 75, 255]))
        temp, frame_contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for contour in frame_contours:
            if self._is_red_score_box(contour):
                    return True, construct_bounding_box_array_from_contour(contour), self._is_score_flipped(contour)
        return False, None, False

    def _is_red_score_box(self, contour):
        if cv2.contourArea(contour) > 1000:
            [x, y, w, h] = cv2.boundingRect(contour)
            return (1.85 <= w / h <= 2.15 and
                    (y / self.frame_image.shape[0] > .77 or y / self.frame_image.shape[0] < .1) and
                    (.55 > x / self.frame_image.shape[1] > .35))

    def _is_score_flipped(self, contour):
        [x, y, w, h] = cv2.boundingRect(contour)
        return x / self.frame_image.shape[1] > .45

    def check_for_score_box(self):  # TODO
        return True

    def get_match_number(self):  # TODO
        return None

    def get_score_state(self):
        if self.flipped:
            return ScoreState.factory_normal(self._get_time(), self._get_score(Side.BLUE), self._get_score(Side.RED),
                              self._get_scale_control(), self._get_switch_control(Side.RED),
                              self._get_switch_control(Side.BLUE))
        else:
            return ScoreState.factory_normal(self._get_time(), self._get_score(Side.RED), self._get_score(Side.BLUE),
                              self._get_scale_control(), self._get_switch_control(Side.RED),
                              self._get_switch_control(Side.BLUE))

    def _get_score(self, side):
        if side == Side.RED:
            score_roi = self._roi_template_point_to_frame((492, 47), 146, 69)
        else:
            score_roi = self._roi_template_point_to_frame((642, 47), 146, 69)

        return self._read_number_from_roi(score_roi, self.score_digit_classifier, self._is_score_digit)

    def _get_time(self):
        if self.is_match_under_review():
            return 0
        time_roi = self._roi_template_point_to_frame((617, 13), 49, 26)
        return self._adjust_time(self._read_number_from_roi(time_roi, self.time_digit_classifier, self._is_time_digit))

    def _adjust_time(self, time):
        if 0 < time < 15 and self._auto_time_check(cv2.mean(self._roi_template_point_to_frame((695, 30), 8, 8))):
            time += 135
        elif time == 0:
            if self._auto_time_check(
                    cv2.mean(self._roi_template_point_to_frame((695, 30), 8, 8))) and not self._is_color_green(
                    cv2.mean((self._roi_template_point_to_frame((494, 19), 2, 2)))):  # before match
                time = 150
            elif self._auto_time_check(
                    cv2.mean(self._roi_template_point_to_frame((695, 30), 8, 8))) and self._is_color_green(cv2.mean(
                    (self._roi_template_point_to_frame((494, 19), 2, 2)))):  # unlucky one frame between 0 and 135
                time = 135

        return time

    def _read_number_from_roi(self, roi_image, knn_classifier, is_digit_function):
        digit_mask = cv2.inRange(roi_image, knn_classifier.mask_lower_limit, knn_classifier.mask_upper_limit)
        digit_contours = self._get_number_contours(digit_mask, is_digit_function)
        if len(digit_contours) == 0:
            cv2.imwrite('C:\\Users\\darkd\\Documents\\ScoreProject\\log\\roi_error%i.png' % random.randint(1, 1000000), roi_image)
            raise NoDigitContoursException('ERROR: No digit contours')

        number_value = 0
        for contour_index, contour in enumerate(digit_contours):
            [x, y, w, h] = cv2.boundingRect(contour)
            digit_roi = roi_image[y:y + h, x:x + w]

            sample_array = knn_classifier.mask_to_sample_array(
                knn_classifier.image_to_scaled_mask(digit_roi))

            number_value += (10 ** (len(digit_contours) - 1 - contour_index)) * knn_classifier.predict_digit(
                sample_array.reshape(1, -1))
        return int(number_value)

    def _get_number_contours(self, mask_image, is_digit_function):
        temp, contours, hierarchy = cv2.findContours(mask_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        accepted_contours = []
        contours_x_values = []
        for contour_index, contour in enumerate(contours):
            if is_digit_function(contour, mask_image) and hierarchy[0][contour_index, 3] == -1:
                accepted_contours.append(np.array(contour, dtype=np.int32))
                contours_x_values.append(cv2.boundingRect(contour)[0])

        return np.array(accepted_contours)[np.array(contours_x_values).argsort()]  # sort so left most contour is first

    def _is_score_digit(self, contour, mask_image):
        [x, y, w, h] = cv2.boundingRect(contour)
        return cv2.contourArea(contour) > 100 and .5 < h / mask_image.shape[0] < .6

    def _is_time_digit(self, contour, mask_image):
        [x, y, w, h] = cv2.boundingRect(contour)
        return cv2.contourArea(contour) > 30 and .6 < h / mask_image.shape[0]

    def _transform_template_point(self, x_template_pos, y_template_pos):
        return (self.template_to_frame_transform * np.matrix([[x_template_pos], [y_template_pos], [1]])).astype(int).flatten().tolist()[0]

    def _roi_template_point_to_frame(self, template_point, height, width):
        frame_point = self._transform_template_point(template_point[0], template_point[1])
        return self.frame_image[
               frame_point[1]:frame_point[1] + width,
               frame_point[0]:frame_point[0] + height]

    def _auto_time_check(self, mean_color):
        return 120 < mean_color[0] < 140 and 160 < mean_color[1] < 190 and \
               190 < mean_color[2] <= 225

    def is_match_over(self):
        mean_color = cv2.mean(self._roi_template_point_to_frame((695, 30), 8, 8))
        return 0 <= mean_color[0] < 60 and 0 <= mean_color[1] < 60 and 205 < mean_color[2] <= 255

    def is_match_under_review(self):
        # 10.0, 255.0, 250.35714285714283,
        mean_color = cv2.mean(self._roi_template_point_to_frame((633, 48), 14, 4))
        return 0 <= mean_color[0] < 30 and 220 <= mean_color[1] <= 255 and 210 < mean_color[2] <= 255

    def _get_scale_control(self):
        red_scale_indicator_roi = self._roi_template_point_to_frame((266, 42), 4, 4)
        blue_scale_indicator_roi = self._roi_template_point_to_frame((1008, 42), 4, 4)
        if self.flipped:  # Red becomes blue
            if self._is_color_red(cv2.mean(blue_scale_indicator_roi)):
                return Side.RED
            if self._is_color_blue(cv2.mean(red_scale_indicator_roi)):
                return Side.BLUE
            else:
                return Side.NONE
        else:
            if self._is_color_red(cv2.mean(red_scale_indicator_roi)):
                return Side.RED
            if self._is_color_blue(cv2.mean(blue_scale_indicator_roi)):
                return Side.BLUE
            else:
                return Side.NONE

    def _get_switch_control(self, side):
        if self.flipped:
            if side == Side.RED:
                switch_indicator_roi = self._roi_template_point_to_frame((1008, 73), 4, 4)
                return self._is_color_red(cv2.mean(switch_indicator_roi))
            else:
                switch_indicator_roi = self._roi_template_point_to_frame((266, 73), 4, 4)
                return self._is_color_blue(cv2.mean(switch_indicator_roi))
        else:
            if side == Side.RED:
                switch_indicator_roi = self._roi_template_point_to_frame((266, 73), 4, 4)
                return self._is_color_red(cv2.mean(switch_indicator_roi ))
            else:
                switch_indicator_roi = self._roi_template_point_to_frame((1008, 73), 4, 4)
                return self._is_color_blue(cv2.mean(switch_indicator_roi))



    def _is_color_red(self, mean_color):
        return 0 <= mean_color[0] < 60 and 0 <= mean_color[1] < 60 and 180 < mean_color[2] <= 255

    def _is_color_blue(self, mean_color):
        return 150 < mean_color[0] < 200 and 85 < mean_color[1] < 125 and 0 <= mean_color[2] < 40

    def _is_color_green(self, mean_color):
        return 0 <= mean_color[0] < 45 and 125 < mean_color[1] < 170 and 0 <= mean_color[2] < 70
