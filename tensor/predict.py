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

import pandas as pd
import user_data
from random import randint

CHECKPOINT_PATH = "/home/musik/DATX02/tensor/checkpoints"

def get_checkpoint_state():
    s = tf.train.latest_checkpoint(checkpoint_dir=CHECKPOINT_PATH)
    return int(''.join(ele for ele in s if ele.isdigit()))

def predict(batch_size, user, pulse, timevalue, rate):

    train_classes = user_data.get_songids()

    # Feature columns describe how to use the input.
    my_feature_columns = []
    hashed_feature_column = tf.feature_column.categorical_column_with_hash_bucket(key = 'userid',hash_bucket_size = 100)
    embedding_column = tf.feature_column.embedding_column(categorical_column=hashed_feature_column,dimension=3)
    my_feature_columns.append(embedding_column)
    my_feature_columns.append(tf.feature_column.numeric_column(key='heartrate'))
    my_feature_columns.append(tf.feature_column.numeric_column(key='time'))
    my_feature_columns.append(tf.feature_column.numeric_column(key='rating'))


    # Build 2 hidden layer DNN with 10, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        # Two hidden layers of 10 nodes each.
        hidden_units=[10, 10],
        # The model must choose between 3 classes.
        n_classes=len(train_classes.index),
        model_dir=CHECKPOINT_PATH)

    # Generate predictions from the model
    predict_x = {
        'userid': [user],
        'heartrate': [pulse],
        'time': [timevalue],
        'rating': [rate],
    }


    predictions = classifier.predict(
        input_fn=lambda: user_data.eval_input_fn(predict_x,
                                                 labels=None,
                                                 batch_size=batch_size))


    for pred_dict in predictions:
        class_id = pred_dict['class_ids'][0]
        probability = pred_dict['probabilities']

        # Temporary random return function until training set have enough data
        temp_list = []
        for x in range (10):
            temp_list.append(train_classes.loc[randint(0,(len(train_classes.index)-1))].item())
        return temp_list


