from argparse import _AppendAction

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np


class CBandit:
    def __init__(self, states, actions):
        tf.reset_default_graph()  # Clear the Tensorflow graph.
        self.cBandit = ContextualBandit(states, actions)  # Load the bandits.
        self.myAgent = Agent(lr=0.001, s_size=self.cBandit.num_states, a_size=self.cBandit.num_actions)  # Load the agent.
        self.weights = tf.trainable_variables()[0]  # The weights we will evaluate to look into the network.

        self.e = 0.1  # Set the chance of taking a random action.
        self.init = tf.global_variables_initializer()
        self.rankingIdentifiers = {}
        self.latestRID = 0
        self.sess = tf.Session()
        self.sess.run(self.init)

    def predict(self, s):
        # Choose either a random action or one from our network.
        if np.random.rand(1) < self.e:
            action = np.random.randint(self.cBandit.num_actions)
        else:
            action = self.sess.run(self.myAgent.chosen_action, feed_dict={self.myAgent.state_in: [s]})
        self.latestRID = self.latestRID + 1
        self.rankingIdentifiers[self.latestRID]={'action': action, 'state': s}
        return (action, self.latestRID)

    def train_rid(self, reward, rid):
        # Get data for the ranking id
        s, action = self.rankingIdentifiers[rid]['state'], self.rankingIdentifiers[rid]['action']
        # Update the network.
        feed_dict = {self.myAgent.reward_holder: [reward], self.myAgent.action_holder: [action], self.myAgent.state_in: [s]}
        _, ww = self.sess.run([self.myAgent.update, self.weights], feed_dict=feed_dict)

    def train_no_rid(self, reward, s, action):
        # Update the network.
        feed_dict = {self.myAgent.reward_holder: [reward], self.myAgent.action_holder: [action], self.myAgent.state_in: [s]}
        _, ww = self.sess.run([self.myAgent.update, self.weights], feed_dict=feed_dict)


    def echo(self, p):  # TODO REMOVE
        print(str(p))  # TODO REMOVE


class ContextualBandit:
    def __init__(self, states, actions):
        self.bandits = np.empty(actions, dtype=int)
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
