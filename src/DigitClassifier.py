import numpy as np
import cv2
from sklearn.neighbors import KNeighborsClassifier


class DigitClassifier:
    def __init__(self, train_path, image_size, mask_lower_limit, mask_upper_limit):
        self.train_path = train_path
        self.image_size = image_size
        self.mask_lower_limit = mask_lower_limit
        self.mask_upper_limit = mask_upper_limit
        self.knn_classifier = KNeighborsClassifier(n_neighbors=1)
        self.knn_classifier.fit(self.load_training_data(), np.array([*range(0, 10)]))

    def load_training_data(self):
        training_data = np.empty((0, self.image_size[0]*self.image_size[1]))
        for digit in range(0, 10):
            training_directory = self.train_path + str(digit) + '.png'
            digit_image = cv2.imread(training_directory)
            training_data = np.append(training_data, self.mask_to_sample_array(self.image_to_scaled_mask(digit_image)), axis=0)
        return training_data

    def predict_digit(self, sample_array):
        return self.knn_classifier.predict(sample_array)[0]

    def image_to_scaled_mask(self, digit_image):
        digit_image = cv2.resize(digit_image, self.image_size, interpolation=cv2.INTER_CUBIC)
        return cv2.inRange(digit_image, self.mask_lower_limit, self.mask_upper_limit)

    def mask_to_sample_array(self, mask_image):
        return mask_image.reshape((1, self.image_size[0] * self.image_size[1]))
