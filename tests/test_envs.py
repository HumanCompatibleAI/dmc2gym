"""Tests for DMC environments wrapped by dmc2gym.DMCWrapper.

Test gym.Env environments produced by applying dmc2gym.DMCWrapper on
dm_control.rl.control.Environment instances
"""

from typing import List, Tuple, Union

import dmc2gym
import gym
# import pytest
# from dm_control import suite
from dmc2gym.utils import dmc_task2str
# from dmc2gym.testing import check_env

# dmc2gym.register_suite(suite)

# """Helper methods for tests of custom Gym environments wrapped from DM_Control envs."""

from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, Union

# import gym
# from dmc2gym.utils import dmc_task2str
# from stable_baselines3.common.env_checker import check_env

# Step = Tuple[Any, Optional[float], bool, Mapping[str, Any]]
# Rollout = Sequence[Step]
# """A sequence of 4-tuples (obs, rew, done, info) as returned by `get_rollout`."""


def make_env_fixture(
    skip_fn: Callable[[str], None],
) -> Callable[[Tuple[str, str, Union[str, None]]], gym.Env]:
    """Creates a fixture function, calling `skip_fn` when dependencies are missing.

    For example, in `pytest`, one would use:
        env = pytest.fixture(make_env_fixture(skip_fn=pytest.skip))
    Then any method with an `env` parameter will receive the created environment, with
    the `env_name` parameter automatically passed to the fixture.
    In `unittest`, one would use::
        def skip_fn(msg):
            raise unittest.SkipTest(msg)
        make_env = contextlib.contextmanager(make_env_fixture(skip_fn=skip_fn))
    And then call `with make_env(env_name) as env:` to create environments.

    Args:
        skip_fn: the function called when a dependency is missing to skip the test.

    Returns:
        A method to create Gym environments given their name.
    """

    def f(subtask_identifier: Tuple[str, str, Union[str, None]]) -> gym.Env:
        """Create environment from `subtask_identifier`.

        Args:
            subtask_identifier: A two-element tuple of (domain, task).

        Yields:
            The created environment.

        Raises:
            gym.error.DependencyNotInstalled: if a dependency is missing
                other than MuJoCo (for MuJoCo, the test is instead skipped).
        """
        env = None
        try:
            domain_name, task_name, subtask_name = subtask_identifier
            env = gym.make(
                dmc_task2str(domain_name, task_name),
                # Passing in subtask_name below
                task_kwargs=dict(subtask=subtask_name, random=42),
                environment_kwargs={},
                visualize_reward=False,
            )
            yield env
        except gym.error.DependencyNotInstalled as e:  # pragma: no cover
            if e.args[0].find("mujoco_py") != -1:
                skip_fn("Requires `mujoco_py`, which isn't installed.")
            else:
                raise
        finally:
            if env is not None:
                env.close()

    return f


# def test_sb3_env_check(env: gym.Env):
#     """Tests if custom environments can pass gym env check by stable-baseline3."""
#     check_env(env)

# env = pytest.fixture(rft_test.make_env_fixture(skip_fn=pytest.skip))


# @pytest.mark.parametrize("subtask_identifier", RFT_SUBTASKS)
# class TestEnvs:
#     """Battery of simple tests for environments."""

#     def test_sb3_env_check(self, env: gym.Env):
#         """Apply stable_baselines3.common.env_checker.check_env() to all envs."""
#         rft_test.test_sb3_env_check(env)

#     def test_seed(
#         self,
#         env: gym.Env,
#         subtask_identifier: Tuple[str, str, Union[str, None]],
#     ):
#         """Tests environment seeding."""
#         domain_name, task_name, subtask_name = subtask_identifier
#         env_name = dmc_task2str(domain_name, task_name)
#         seals_test.test_seed(
#             env,
#             env_name=f"{env_name}-{subtask_name}",
#             deterministic_envs=DETERMINISTIC_ENVS,
#         )

#     def test_rollout_schema(self, env: gym.Env):
#         """Tests if environments have correct types on `step()` and `reset()`."""
#         seals_test.test_rollout_schema(env)

#     def test_render(self, env: gym.Env):
#         """Tests `render()` supports modes specified in environment metadata."""
#         seals_test.test_render(env, raises_fn=pytest.raises)
