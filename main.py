# Import dependencies
import numpy as np
import gym
from keras.utils.np_utils import to_categorical as one_hot
from collections import namedtuple
from dqn_model import DoubleQLearningModel, ExperienceReplay


def eps_greedy_policy(q_values, eps):
    '''
    Creates an epsilon-greedy policy
    :param q_values: set of Q-values of shape (num actions,)
    :param eps: probability of taking a uniform random action
    :return: policy of shape (num actions,)
    '''
    # YOUR CODE HERE
    policy = np.ones(q_values.shape) * (eps / len(q_values))
    policy[np.argmax(q_values)] += (1 - eps)

    return policy


def calculate_td_targets(q1_batch, q2_batch, r_batch, t_batch, gamma=.99):
    '''
    Calculates the TD-target used for the loss
    : param q1_batch: Batch of Q(s', a) from online network, shape (N, num actions)
    : param q2_batch: Batch of Q(s', a) from target network, shape (N, num actions)
    : param r_batch: Batch of rewards, shape (N, 1)
    : param t_batch: Batch of booleans indicating if state, s' is terminal, shape (N, 1)
    : return: TD-target, shape (N, 1)
    '''
    # YOUR CODE HERE
    N = q1_batch.shape[0]
    best_actions = np.argmax(q1_batch, axis=1).reshape(N,1) # Nx1
    Q = np.array([q2_batch[s,a] for s,a in enumerate(best_actions)]) # Nx1
    Y = r_batch + gamma * np.logical_not(t_batch) * Q
    return Y


def train_loop_ddqn(model, env, num_episodes, batch_size=64, gamma=.94):
    Transition = namedtuple("Transition", ["s", "a", "r", "next_s", "t"])
    eps = 1.
    eps_end = .1
    eps_decay = .001
    R_buffer = []
    R_avg = []
    for i in range(num_episodes):
        state = env.reset()  # reset to initial state
        state = np.expand_dims(state, axis=0) / 2
        state = state[0][0:-1].reshape(1, 3)
        terminal = False  # reset terminal flag
        ep_reward = 0
        q_buffer = []
        steps = 0
        while not terminal:
            env.render()  # comment this line out if you don't want to / cannot render the environment on your system
            steps += 1
            q_values = model.get_q_values(state)
            q_buffer.append(q_values)
            policy = eps_greedy_policy(q_values.squeeze(), eps)
            action = np.random.choice(num_actions, p=policy)  # sample action from epsilon-greedy policy
            new_state, reward, terminal, _ = env.step(action)  # take one step in the evironment
            new_state = np.expand_dims(new_state, axis=0) / 2
            new_state = new_state[0][0:-1].reshape(1, 3)

            # only use the terminal flag for ending the episode and not for training
            # if the flag is set due to that the maximum amount of steps is reached 
            t_to_buffer = terminal if not steps == 200 else False

            # store data to replay buffer
            replay_buffer.add(Transition(s=state, a=action, r=reward, next_s=new_state, t=t_to_buffer))
            state = new_state
            ep_reward += reward

            # if buffer contains more than 1000 samples, perform one training step
            if replay_buffer.buffer_length > 1000:
                s, a, r, s_, t = replay_buffer.sample_minibatch(batch_size)  # sample a minibatch of transitions
                q_1, q_2 = model.get_q_values_for_both_models(np.squeeze(s_))
                td_target = calculate_td_targets(q_1, q_2, r, t, gamma)
                model.update(s, td_target, a)

        eps = max(eps - eps_decay, eps_end)  # decrease epsilon
        R_buffer.append(ep_reward)

        # running average of episodic rewards
        R_avg.append(.05 * R_buffer[i] + .95 * R_avg[i - 1]) if i > 0 else R_avg.append(R_buffer[i])
        print('Episode: ', i, 'Reward:', ep_reward, 'Epsilon', eps, 'mean q', np.mean(np.array(q_buffer)))

        # if running average > 195, the task is considerd solved
        if R_avg[-1] > 195:
            return R_buffer, R_avg
    return R_buffer, R_avg


# Create the environment
env = gym.make("CartPole-v0")

# Initializations
num_actions = env.action_space.n
obs_dim = env.observation_space.shape[0] - 1

# Our Neural Netork model used to estimate the Q-values
model = DoubleQLearningModel(state_dim=obs_dim, action_dim=num_actions, learning_rate=1e-4)

# Create replay buffer, where experience in form of tuples <s,a,r,s',t>, gathered from the environment is stored
# for training
replay_buffer = ExperienceReplay(state_size=obs_dim)

# Train
num_episodes = 1200
batch_size = 128
R, R_avg = train_loop_ddqn(model, env, num_episodes, batch_size) #num_episodes