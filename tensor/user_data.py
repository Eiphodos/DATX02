import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

import pandas as pd
import tensorflow as tf

TRAIN_PATH = "/home/musik/DATX02/tensor/training_data/training.csv"

CSV_COLUMN_NAMES = ['userid', 'heartrate',
                    'time', 'rating', 'songid']

def load_data(y_name='songid'):
    """Returns the iris dataset as (train_x, train_y), (test_x, test_y)."""
    train_path = TRAIN_PATH

    train = pd.read_csv(train_path, names=CSV_COLUMN_NAMES, header=0)
    songs = train.pop(y_name).astype('category')
    songcodes = songs.cat.codes.astype('int32')
    d = {'songid': songs.cat.categories.tolist() }
    classes = pd.DataFrame.from_dict(d)
    train_x, train_y, train_classes = train, songcodes, classes
    return (train_x, train_y, train_classes)

def get_songids(y_name='songid'):
    """Returns the iris dataset as (train_x, train_y), (test_x, test_y)."""
    train_path = TRAIN_PATH
    train = pd.read_csv(train_path, names=CSV_COLUMN_NAMES, header=0)
    songs = train.pop(y_name).astype('category')
    d = {'songid': songs.cat.categories.tolist() }
    classes = pd.DataFrame.from_dict(d)
    return classes


def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the read end of the pipeline.
    return dataset.make_one_shot_iterator().get_next()


def eval_input_fn(features, labels, batch_size):
    """An input function for evaluation or prediction"""
    features=dict(features)
    if labels is None:
        # No labels, use only features.
        inputs = features
    else:
        inputs = (features, labels)

    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)

    # Return the read end of the pipeline.
    return dataset.make_one_shot_iterator().get_next()


# The remainder of this file contains a simple example of a csv parser,
#     implemented using a the `Dataset` class.

# `tf.parse_csv` sets the types of the outputs to match the examples given in
#     the `record_defaults` argument.
CSV_TYPES = [[0.0], [0.0], [0.0], [0.0], [0]]

def _parse_line(line):
    # Decode the line into its fields
    fields = tf.decode_csv(line, record_defaults=CSV_TYPES)

    # Pack the result into a dictionary
    features = dict(zip(CSV_COLUMN_NAMES, fields))

    # Separate the label from the features
    label = features.pop('Species')

    return features, label


def csv_input_fn(csv_path, batch_size):
    # Create a dataset containing the text lines.
    dataset = tf.data.TextLineDataset(csv_path).skip(1)

    # Parse each line.
    dataset = dataset.map(_parse_line)

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the read end of the pipeline.
    return dataset.make_one_shot_iterator().get_next()