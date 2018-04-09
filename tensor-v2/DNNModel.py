from __future__ import absolute_import, division, print_function

import os
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.contrib.eager as tfe

tf.enable_eager_execution()

class DNNModel:
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation="relu", input_shape=(3,)),
        tf.keras.layers.Dense(10, activation="relu"),
        tf.keras.layers.Dense(3)
    ])

    def train(self, csv_path):
        dataset = tf.data.TextLineDataset(csv_path)
        dataset = dataset.map(self.parse_csv)
        dataset = dataset.batch(32) # Limit batch size to train model faster

        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)

        loss_results = []
        accuracy_results = []

        num_epochs = 101

        for epoch in range(num_epochs):
            epoch_loss_avg = tfe.metrics.Mean()
            epoch_accuracy = tfe.metrics.Accuracy()

            for x, y in tfe.Iterator(dataset):
                grads = self.grad(self.model, x, y)
                optimizer.apply_gradients(zip(grads, self.model.variables), global_step=tf.train.get_or_create_global_step())

                epoch_loss_avg(self.loss(self.model, x, y))
                epoch_accuracy(tf.argmax(self.model(x), axis=1, output_type=tf.int32), y)

            loss_results.append(epoch_loss_avg.result())
            accuracy_results.append(epoch_accuracy.result())

        return loss_results, accuracy_results

    def eval(self, csv_path):
        dataset = tf.data.TextLineDataset(csv_path)
        dataset = dataset.map(self.parse_csv)
        dataset = dataset.batch(32)

        accuracy = tfe.metrics.Accuracy()

        for x, y in tfe.Iterator(dataset):
            prediction = tf.argmax(self.model(x), axis=1, output_type=tf.int32)
            accuracy(prediction, y)

        return accuracy.result()

    def predict(self, data_matrix):
        # BPM buckets
        class_ids = ["0-30", "31-50", "51-70", "71-90", "91-110", "111-130", "131-150", "151-170", "171-190", "191-210", "211+"]

        dataset = tf.convert_to_tensor(data_matrix)

        predictions = self.model(dataset)

        results = []

        for i, logits in enumerate(predictions):
            class_idx = tf.argmax(logits).numpy()
            name = class_ids[class_idx]
            results.append(name)

        return results

    def loss(self, model, x, y):
        y_ = model(x)
        return tf.losses.sparse_softmax_cross_entropy(labels=y, logits=y_)

    def grad(self, model, inputs, targets):
        with tfe.GradientTape() as tape:
            loss_value = self.loss(model, inputs, targets)
        return tape.gradient(loss_value, model.variables)

    def parse_csv(self, line):
        # user_id:string, time:int, heart_rate:int, bpm:int
        defaults = [[""], [0], [0], [0]]

        parsed_line = tf.decode_csv(line, defaults)

        features = tf.reshape(parsed_line[:-1], shape=(3,))

        label = tf.reshape(parsed_line[-1], shape=())

        return features, label