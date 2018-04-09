from __future__ import absolute_import, division, print_function

import os
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.contrib.eager as tfe

tf.enable_eager_execution()


class LRModel:

    def __init__(self, model_dir):
        user_column = tf.feature_column.categorical_column_with_hash_bucket(key='user_id',hash_bucket_size=100)
        time_column = tf.feature_column.numeric_column("time")
        heart_rate_column = tf.feature_column.numeric_column("heart_rate")

        bpm_num_column = tf.feature_column.numeric_column("bpm")
        bpm_buck_column = tf.feature_column.bucketized_column(source_column=bpm_num_column, boundaries=[30, 50, 70, 90, 110, 130, 150, 170, 190, 210])


        self.estimator = tf.estimator.LinearRegressor(feature_columns=[user_column, time_column, heart_rate_column, bpm_buck_column], model_dir=model_dir)

    def train(self, csv_path):
        train_input_fn = self.csv_to_dataset(csv_path)

        result = self.estimator.train(input_fn=train_input_fn)

        return result

    def eval(self, csv_path):
        eval_input_fn = self.csv_to_dataset(csv_path)

        evaluation = self.estimator.evaluate(input_fn=eval_input_fn)

        return evaluation

    def predict(self, data_matrix):
        pred_input_fn = tf.convert_to_tensor(data_matrix)

        prediction = self.estimator.predict(input_fn=pred_input_fn, predict_keys="bpm")

        return prediction

    def csv_to_dataset(self, csv_path):
        dataset = tf.data.TextLineDataset(csv_path)
        dataset = dataset.map(self.parse_csv)
        dataset = dataset.batch(32)

        return dataset

    def parse_csv(self, line):
        # user_id:string, time:int, heart_rate:int, bpm:int
        defaults = [[""], [0], [0], [0]]

        parsed_line = tf.decode_csv(line, defaults)

        features = tf.reshape(parsed_line[:-1], shape=(3,))

        label = tf.reshape(parsed_line[-1], shape=())

        return features, label