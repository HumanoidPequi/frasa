import gymnasium as gym
import frasa_env
import numpy as np

from stable_baselines3.common.vec_env import DummyVecEnv
from sbx import PPO

gym.register_envs(frasa_env)


def make_env():
    return gym.make("frasa-standup-v0")


vec_env = DummyVecEnv([make_env])

print("Vec observation space:")
print(vec_env.observation_space)
print("shape:", vec_env.observation_space.shape)
print("dtype:", vec_env.observation_space.dtype)

obs = vec_env.reset()

print("\nVec reset:")
print("type:", type(obs))
print("shape:", obs.shape)
print("dtype:", obs.dtype)
print("obs:", obs)

print("\nCriando PPO...")

model = PPO(
    "MlpPolicy",
    vec_env,
    n_steps=512,
    batch_size=64,
    n_epochs=2,
    learning_rate=5e-5,
    gamma=0.998,
    gae_lambda=0.95,
    ent_coef=0.0001,
    use_sde=False,
    verbose=1,
    device="cpu",
)

print("\nPPO criado!")

vec_env.close()
