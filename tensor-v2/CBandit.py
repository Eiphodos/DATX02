from argparse import _AppendAction

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np


class CBandit:
    def __init__(self, states):
        tf.reset_default_graph()  # Clear the Tensorflow graph.
        self.cBandit = ContextualBandit(states)  # Load the bandits.
        self.myAgent = Agent(lr=0.001, s_size=self.cBandit.num_states, a_size=self.cBandit.num_actions)  # Load the agent.
        self.weights = tf.trainable_variables()[0]  # The weights we will evaluate to look into the network.

        self.e = 0.1  # Set the chance of taking a random action.
        self.init = tf.global_variables_initializer()

        self.sess = tf.Session()
        self.sess.run(self.init)

    def predict(self, s):
        # Launch the tensorflow graph

        # Choose either a random action or one from our network.
        if np.random.rand(1) < self.e:
            print("random")  # TODO REMOVE
            action = np.random.randint(self.cBandit.num_actions)
        else:
            print("chosen")  # TODO REMOVE
            action = self.sess.run(self.myAgent.chosen_action, feed_dict={self.myAgent.state_in: [s]})
        return action

    def train(self, s, action, reward):
        # Update the network.
        feed_dict = {self.myAgent.reward_holder: [reward], self.myAgent.action_holder: [action], self.myAgent.state_in: [s]}
        _, ww = self.sess.run([self.myAgent.update, self.weights], feed_dict=feed_dict)
        print(str(ww))  # TODO REMOVE

    def echo(self, p):  # TODO REMOVE
        print(str(p))  # TODO REMOVE


class ContextualBandit:
    def __init__(self, states):
        self.bandits = np.array([0, 1])
        self.num_states = states
        self.num_actions = self.bandits.__len__()


class Agent:
    def __init__(self, lr, s_size, a_size):
        # These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        self.state_in = tf.placeholder(shape=[1], dtype=tf.int32)
        state_in_OH = slim.one_hot_encoding(self.state_in, s_size)
        output = slim.fully_connected(state_in_OH, a_size,
                                      biases_initializer=None, activation_fn=tf.nn.sigmoid,
                                      weights_initializer=tf.ones_initializer())
        self.output = tf.reshape(output, [-1])
        self.chosen_action = tf.argmax(self.output, 0)

        # The next six lines establish the training procedure. We feed the reward and chosen action into the network
        # to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[1], dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[1], dtype=tf.int32)
        self.responsible_weight = tf.slice(self.output, self.action_holder, [1])
        self.loss = -(tf.log(self.responsible_weight) * self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)

