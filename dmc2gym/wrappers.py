# MODIFIED BY Yawen Duan (https://github.com/kmdanielduan) to be able to 
# use `suite_module` to load environments from a dm_control based suite


from gym import core, spaces
from dm_env import specs
import numpy as np

from gym.utils import seeding


def _spec_to_box(spec):
    def extract_min_max(s):
        assert s.dtype == np.float64 or s.dtype == np.float32
        dim = np.int(np.prod(s.shape))
        if type(s) == specs.Array:
            bound = np.inf * np.ones(dim, dtype=np.float64)
            return -bound, bound
        elif type(s) == specs.BoundedArray:
            zeros = np.zeros(dim, dtype=np.float64)
            return s.minimum + zeros, s.maximum + zeros

    mins, maxs = [], []
    for s in spec:
        mn, mx = extract_min_max(s)
        mins.append(mn)
        maxs.append(mx)
    low = np.concatenate(mins, axis=0)
    high = np.concatenate(maxs, axis=0)
    assert low.shape == high.shape
    return spaces.Box(low, high, dtype=np.float64)


def _flatten_obs(obs):
    obs_pieces = []
    for v in obs.values():
        flat = np.array([v]) if np.isscalar(v) else v.ravel()
        obs_pieces.append(flat)
    return np.concatenate(obs_pieces, axis=0)


class DMCWrapper(core.Env):
    def __init__(
        self,
        # suite module
        suite_module,
        # env kwargs
        domain_name,
        task_name,
        task_kwargs=None,
        environment_kwargs=None,
        visualize_reward=False,
        # step_kwargs
        frame_skip=1,
        from_pixels=False,
        # render_kwargs
        height=84,
        width=84,
        camera_id=0,
        # observation_kwargs
        channels_first=True
    ):
        assert isinstance(task_kwargs, dict) and 'random' in task_kwargs, \
            "task_kwargs should be a dictionary with a specified seed"
        self._from_pixels = from_pixels
        self._frame_skip = frame_skip
        self._channels_first = channels_first

        # set render kwargs
        self.render_kwargs = dict(
            height=height,
            width=width,
            camera_id=camera_id,
        )

        # create task
        self._env = suite_module.load(
            domain_name=domain_name,
            task_name=task_name,
            task_kwargs=task_kwargs,
            environment_kwargs=environment_kwargs,
            visualize_reward=visualize_reward
        )

        # setup metadata for rendering since dm_control is based on MuJoCo Physics
        # options from gym.envs.mujoco.mujoco_env
        self.metadata = {
            "render.modes": ["human", "rgb_array", "grey", "notebook"],
            # "video.frames_per_second": int(np.round(1.0 / self.dt)),
        }

        # attribute in gym.Env a default reward range set to [-inf,+inf] already exists. 
        # Set it if you want a narrower range.
        self.reward_range = (-float("inf"), float("inf"))

        # true and normalized action spaces
        self._true_action_space = _spec_to_box([self._env.action_spec()])
        self._norm_action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=self._true_action_space.shape,
            dtype=np.float64
        )

        # create observation space
        if from_pixels:
            shape = [3, height, width] if channels_first else [height, width, 3]
            self._observation_space = spaces.Box(
                low=0, high=255, shape=shape, dtype=np.uint8
            )
        else:
            self._observation_space = _spec_to_box(
                self._env.observation_spec().values()
            )
            
        self._state_space = _spec_to_box(
                self._env.observation_spec().values()
        )
        
        self.current_state = None

        # set seed
        self.seed(seed=task_kwargs.get('random', 42))

    def __getattr__(self, name):
        return getattr(self._env, name)

    def _get_obs(self, time_step):
        if self._from_pixels:
            obs = self.render(mode="rgb_array")
            if self._channels_first:
                obs = obs.transpose(2, 0, 1).copy()
        else:
            obs = _flatten_obs(time_step.observation)
        return obs

    def _convert_action(self, action):
        action = action.astype(np.float64)
        true_delta = self._true_action_space.high - self._true_action_space.low
        norm_delta = self._norm_action_space.high - self._norm_action_space.low
        action = (action - self._norm_action_space.low) / norm_delta
        action = action * true_delta + self._true_action_space.low
        action = action.astype(np.float64)
        return action

    @property
    def observation_space(self):
        return self._observation_space

    @property
    def state_space(self):
        return self._state_space

    @property
    def action_space(self):
        return self._norm_action_space
    
    @property
    def np_random(self):
        """Returns the np.random.RandomState instance of `self._env.task._random`"""
        return self._env.task._random

    def seed(self, seed=None):
        """Wrapper seeding sets the seed in `self._env.task` using the seeding scheme in `gym.utils.seeding`
        Note this will results in different seeding schema between dm_control-only and wrapperd environments"""
        self._env.task._random, seed = seeding.np_random(seed)

        return [seed]

    def step(self, action):
        assert self._norm_action_space.contains(action)
        action = self._convert_action(action)
        assert self._true_action_space.contains(action)
        reward = float(0)
        extra = {'internal_state': self._env.physics.get_state().copy()}

        for _ in range(self._frame_skip):
            time_step = self._env.step(action)
            reward += time_step.reward or float(0)
            done = time_step.last()
            if done:
                break
        obs = self._get_obs(time_step)
        self.current_state = _flatten_obs(time_step.observation)
        extra['discount'] = time_step.discount
        return obs, reward, done, extra

    def reset(self):
        time_step = self._env.reset()
        self.current_state = _flatten_obs(time_step.observation)
        obs = self._get_obs(time_step)
        return obs

    def render(self, mode='rgb_array', height=None, width=None, camera_id=0, **kwargs):
        img = self._env.physics.render(
            height=self.render_kwargs['height'] if height is None else height, 
            width=self.render_kwargs['width'] if width is None else width, 
            camera_id=self.render_kwargs['camera_id'] if camera_id is None else camera_id, 
            **kwargs
        )

        if mode in ['rgb', 'rgb_array']:
            return img.astype(np.uint8)
        elif mode in ['gray', 'grey']:
            return img.mean(axis=-1, keepdims=True).astype(np.uint8)
        elif mode == 'notebook':
            from IPython.display import display
            from PIL import Image
            img = Image.fromarray(img, "RGB")
            display(img)
            return img
        elif mode == 'human':
            from PIL import Image
            return Image.fromarray(img)
        else:
            raise NotImplementedError(f"`{mode}` mode is not implemented")
