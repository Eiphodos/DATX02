from __future__ import absolute_import, division, print_function

import os
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.contrib.eager as tfe

from collections import namedtuple

sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer


FeatureColumn = namedtuple("FeatureColumn", "name column")

class DNNModel:
    output_type = Bucketizer.BucketType.PULSE

    # 5,1

    # output_column is a FeatureColumn (a sort of struct), easy to create using the functions at the bottom
    def __init__(self, model_dir, output_type):
        self.output_type = output_type
        self.checkpoint_path = model_dir
        hashed_user_column = tf.feature_column.categorical_column_with_hash_bucket(key='user_id', hash_bucket_size=100, dtype=tf.string)
        user_column = tf.feature_column.embedding_column(categorical_column=hashed_user_column, dimension=3)
        time_column = tf.feature_column.numeric_column("time")
        heart_rate_column = tf.feature_column.numeric_column("heart_rate")
        rating_column = tf.feature_column.numeric_column("rating")

        classes = Bucketizer.getNumberOfClassesForType(self.output_type)

        self.estimator = tf.estimator.DNNClassifier(feature_columns=[user_column, time_column, heart_rate_column, rating_column],
                                                    hidden_units=[5,1],
                                                    n_classes=classes,
                                                    optimizer=tf.train.GradientDescentOptimizer(learning_rate=0.01),
                                                    model_dir=model_dir)

    def train(self, features, labels):
        bucketized_labels = Bucketizer.getLabelsBucket(labels=labels, type=self.output_type)

        result = self.estimator.train(input_fn=lambda:self.train_input_fn(features=features, labels=bucketized_labels, batch_size=32))

        return result

    def eval(self, features, labels):
        bucketized_labels = Bucketizer.getLabelsBucket(labels=labels, type=self.output_type)

        evaluation = self.estimator.evaluate(input_fn=lambda:self.train_input_fn(features=features, labels=bucketized_labels, batch_size=32))

        return evaluation

    def predict(self, data_matrix):
        prediction = self.estimator.predict(input_fn=lambda:self.pred_input_fn(features=data_matrix, batch_size=32))

        return prediction

    def pred_input_fn(self, features, batch_size):
        inputs = dict(features)

        # Convert the inputs to a Dataset.
        dataset = tf.data.Dataset.from_tensor_slices(inputs)

        # Batch the examples
        assert batch_size is not None, "batch_size must not be None"
        dataset = dataset.batch(batch_size)

        # Return the dataset.
        return dataset

    def train_input_fn(self, features, labels, batch_size):
        """An input function for training"""
        # Convert the inputs to a Dataset.
        dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

        # Shuffle, repeat, and batch the examples.
        #dataset = dataset.shuffle(1000).repeat().batch(batch_size)
        dataset = dataset.shuffle(100)
        dataset = dataset.batch(batch_size=batch_size)
        # Return the dataset.
        return dataset.make_one_shot_iterator().get_next()

    # Returns the number of the latest checkpoint
    def get_checkpoint_state(self):
        s = tf.train.latest_checkpoint(checkpoint_dir=self.checkpoint_path)
        return int(''.join(ele for ele in s if ele.isdigit()))


'''
model = DNNModel(model_dir="", output_type=Bucketizer.BucketType.PULSE)

train_x = {
    'user_id': ["userid1","userid3","userid1","userid1","userid2","userid1","userid1","userid1","userid3","userid2"],
    'time': [1000,500,250,700,900,450,123,900,1000,600],
    'heart_rate': [100,50,25,67,98,123,150,175,35,50]
}

train_labels = [100,150,75,87,90,210,125,55,201,20]

res = model.train(features=train_x, labels=train_labels)

predict_x = {
    'user_id': ["userid1"],
    'time': [1000],
    'heart_rate': [55],
}

pred = model.predict(data_matrix=predict_x)

for p in pred:
    for c in p["class_ids"]:
        print(c)
        print(p['probabilities'][c])
'''