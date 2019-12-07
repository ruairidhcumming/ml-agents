from typing import Dict, List

from mlagents.envs.base_unity_environment import BaseUnityEnvironment
from mlagents.envs.env_manager import EnvManager, EnvironmentStep
from mlagents.envs.timers import timed
from mlagents.envs.action_info import ActionInfo
from mlagents.envs.brain import BrainParameters
from mlagents.envs.side_channel.float_properties_channel import FloatPropertiesChannel


class SimpleEnvManager(EnvManager):
    """
    Simple implementation of the EnvManager interface that only handles one BaseUnityEnvironment at a time.
    This is generally only useful for testing; see SubprocessEnvManager for a production-quality implementation.
    """

    def __init__(
        self, env: BaseUnityEnvironment, float_prop_channel: FloatPropertiesChannel
    ):
        super().__init__()
        self.shared_float_properties = float_prop_channel
        self.env = env
        self.previous_step: EnvironmentStep = EnvironmentStep(None, {}, None)
        self.previous_all_action_info: Dict[str, ActionInfo] = {}

    def step(self) -> List[EnvironmentStep]:

        all_action_info = self._take_step(self.previous_step)
        self.previous_all_action_info = all_action_info

        actions = {}
        values = {}
        for brain_name, action_info in all_action_info.items():
            actions[brain_name] = action_info.action
            values[brain_name] = action_info.value
        all_brain_info = self.env.step(vector_action=actions, value=values)
        step_brain_info = all_brain_info

        step_info = EnvironmentStep(
            self.previous_step.current_all_brain_info,
            step_brain_info,
            self.previous_all_action_info,
        )
        self.previous_step = step_info
        return [step_info]

    def reset(
        self, config: Dict[str, float] = None
    ) -> List[EnvironmentStep]:  # type: ignore
        if config is not None:
            for k, v in config.items():
                self.shared_float_properties.set_property(k, v)
        all_brain_info = self.env.reset()
        self.previous_step = EnvironmentStep(None, all_brain_info, None)
        return [self.previous_step]

    @property
    def external_brains(self) -> Dict[str, BrainParameters]:
        return self.env.external_brains

    @property
    def get_properties(self) -> Dict[str, float]:
        reset_params = {}
        for k in self.shared_float_properties.list_properties():
            reset_params[k] = self.shared_float_properties.get_property(k)
        return reset_params

    def close(self):
        self.env.close()

    @timed
    def _take_step(self, last_step: EnvironmentStep) -> Dict[str, ActionInfo]:
        all_action_info: Dict[str, ActionInfo] = {}
        for brain_name, brain_info in last_step.current_all_brain_info.items():
            all_action_info[brain_name] = self.policies[brain_name].get_action(
                brain_info
            )
        return all_action_info
