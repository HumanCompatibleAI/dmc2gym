# MODIFIED BY Yawen Duan (https://github.com/kmdanielduan)
# moving the whole register process to registration.py

import gym

from dmc2gym.registration import register_env, register_suite
from dmc2gym.wrappers import DMCWrapper
from dmc2gym.utils import dmc_task2str


__all__ = ["DMCWrapper", "register_suite", "register_env", "dmc_task2str"]

