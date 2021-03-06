from typing import List
import logging
import numpy as np
from unittest import mock

from mlagents.envs.communicator_objects.agent_info_pb2 import AgentInfoProto
from mlagents.envs.communicator_objects.observation_pb2 import (
    ObservationProto,
    NONE as COMPRESSION_TYPE_NONE,
)
from mlagents.envs.brain import BrainInfo, BrainParameters

test_brain = BrainParameters(
    brain_name="test_brain",
    vector_observation_space_size=3,
    camera_resolutions=[],
    vector_action_space_size=[],
    vector_action_descriptions=[],
    vector_action_space_type=1,
)


def _make_agent_info_proto(vector_obs: List[float]) -> AgentInfoProto:
    obs = ObservationProto(
        float_data=ObservationProto.FloatData(data=vector_obs),
        shape=[len(vector_obs)],
        compression_type=COMPRESSION_TYPE_NONE,
    )
    agent_info_proto = AgentInfoProto(observations=[obs])
    return agent_info_proto


@mock.patch.object(np, "nan_to_num", wraps=np.nan_to_num)
@mock.patch.object(logging.Logger, "warning")
def test_from_agent_proto_nan(mock_warning, mock_nan_to_num):
    agent_info_proto = _make_agent_info_proto([1.0, 2.0, float("nan")])

    brain_info = BrainInfo.from_agent_proto(1, [agent_info_proto], test_brain)
    # nan gets set to 0.0
    expected = [1.0, 2.0, 0.0]
    assert (brain_info.vector_observations == expected).all()
    mock_nan_to_num.assert_called()
    mock_warning.assert_called()


@mock.patch.object(np, "nan_to_num", wraps=np.nan_to_num)
@mock.patch.object(logging.Logger, "warning")
def test_from_agent_proto_inf(mock_warning, mock_nan_to_num):
    agent_info_proto = _make_agent_info_proto([1.0, float("inf"), 0.0])

    brain_info = BrainInfo.from_agent_proto(1, [agent_info_proto], test_brain)
    # inf should get set to float32_max
    float32_max = np.finfo(np.float32).max
    expected = [1.0, float32_max, 0.0]
    assert (brain_info.vector_observations == expected).all()
    mock_nan_to_num.assert_called()
    # We don't warn on inf, just NaN
    mock_warning.assert_not_called()


@mock.patch.object(np, "nan_to_num", wraps=np.nan_to_num)
@mock.patch.object(logging.Logger, "warning")
def test_from_agent_proto_fast_path(mock_warning, mock_nan_to_num):
    """
    Check that all finite values skips the nan_to_num call
    """
    agent_info_proto = _make_agent_info_proto([1.0, 2.0, 3.0])

    brain_info = BrainInfo.from_agent_proto(1, [agent_info_proto], test_brain)
    expected = [1.0, 2.0, 3.0]
    assert (brain_info.vector_observations == expected).all()
    mock_nan_to_num.assert_not_called()
    mock_warning.assert_not_called()
