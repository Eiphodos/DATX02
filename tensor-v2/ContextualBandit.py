from argparse import _AppendAction

import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np


class ContextualBandit:
    def __init__(self):
        self.state = 0
        self.bandits = np.array([0, 1])
        #self.num_bandits = self.bandits.shape[0]
        self.num_states = 7
        self.num_actions = self.bandits.__len__()

    def getBandit(self):
        # Assumption that the BMP and time can be placed in a number of "buckets"
        self.state = np.random.randint(0, self.num_states)  # Returns a random state for each episode.
        return self.state

    def pullArm(self, action):
        # Get a random number.
        # bandit = self.bandits[self.state, action]
        if self.state % 2 == action:
            # return a positive reward.
            return 1
        else:
            # return a negative reward
            return -1


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

        # The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        # to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[1], dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[1], dtype=tf.int32)
        self.responsible_weight = tf.slice(self.output, self.action_holder, [1])
        self.loss = -(tf.log(self.responsible_weight) * self.reward_holder)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=lr)
        self.update = optimizer.minimize(self.loss)


tf.reset_default_graph()  # Clear the Tensorflow graph.

cBandit = ContextualBandit()  # Load the bandits.
myAgent = Agent(lr=0.001, s_size=cBandit.num_states, a_size=cBandit.num_actions)  # Load the agent.
weights = tf.trainable_variables()[0]  # The weights we will evaluate to look into the network.

total_episodes = 10000  # Set total number of episodes to train agent on.
total_reward = np.zeros([cBandit.num_states, cBandit.num_actions])  # Set scoreboard for bandits to 0.
e = 0.1  # Set the chance of taking a random action.

init = tf.global_variables_initializer()

# Launch the tensorflow graph
with tf.Session() as sess:

    sess.run(init)
    i = 0
    while i < total_episodes:

        s = cBandit.getBandit()  # Get a state from the environment.

        # Choose either a random action or one from our network.
        if np.random.rand(1) < e:
            action = np.random.randint(cBandit.num_actions)
        else:
            action = sess.run(myAgent.chosen_action, feed_dict={myAgent.state_in: [s]})

        reward = cBandit.pullArm(action)  # Get our reward for taking an action given a bandit.

        # Update the network.
        feed_dict = {myAgent.reward_holder: [reward], myAgent.action_holder: [action], myAgent.state_in: [s]}
        _, ww = sess.run([myAgent.update, weights], feed_dict=feed_dict)

        # Update our running tally of scores.
        total_reward[s, action] += reward

        if i % 500 == 0:
            print("Mean reward for each of the " + str(cBandit.num_states) + " bandits: " + str(
                np.mean(total_reward, axis=1)))
        i += 1

    for a in range(cBandit.num_states):
        print("The agent thinks action " + str(np.argmax(ww[a]) + 1) + " for bandit " + str(a + 1) + " is the most promising....")
        print(str(ww[a]))