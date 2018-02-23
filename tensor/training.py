from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import argparse
import tensorflow as tf

import user_data


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=1000, type=int,
                    help='number of training steps')

def main(argv):
    args = parser.parse_args(argv[1:])

    # Fetch the data
    (train_x, train_y, train_classes) = user_data.load_data()

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
        model_dir='checkpoints')

    # Train the Model.
    classifier.train(
        input_fn=lambda:user_data.train_input_fn(train_x, train_y,
                                                 args.batch_size),
        steps=args.train_steps)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)
