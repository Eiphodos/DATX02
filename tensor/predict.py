from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'

import argparse
import tensorflow as tf


import user_data


def predict(batch_size, user, pulse, timevalue):


    # Feature columns describe how to use the input.
    my_feature_columns = []
    hashed_feature_column = tf.feature_column.categorical_column_with_hash_bucket(key = 'userid',hash_bucket_size = 100)
    embedding_column = tf.feature_column.embedding_column(categorical_column=hashed_feature_column,dimension=3)
    my_feature_columns.append(embedding_column)
    my_feature_columns.append(tf.feature_column.numeric_column(key='heartrate'))
    my_feature_columns.append(tf.feature_column.numeric_column(key='time'))

    # Build 2 hidden layer DNN with 10, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        # Two hidden layers of 10 nodes each.
        hidden_units=[10, 10],
        # The model must choose between 3 classes.
        n_classes=3,
        model_dir=r"C:\Users\David\Documents\GitHub\DATX02\tensor\checkpoints")


    # Generate predictions from the model
    predict_x = {
        'userid': [user],
        'heartrate': [pulse],
        'time': [timevalue],
    }

    predictions = classifier.predict(
        input_fn=lambda: user_data.eval_input_fn(predict_x,
                                                 labels=None,
                                                 batch_size=batch_size))

    for pred_dict in predictions:
        class_id = pred_dict['class_ids'][0]
        probability = pred_dict['probabilities'][class_id]
        return user_data.SONGID[class_id]

