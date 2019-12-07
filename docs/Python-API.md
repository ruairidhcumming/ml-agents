# Unity ML-Agents Python Interface and Trainers

The `mlagents` Python package is part of the [ML-Agents
Toolkit](https://github.com/Unity-Technologies/ml-agents). `mlagents` provides a
Python API that allows direct interaction with the Unity game engine as well as
a collection of trainers and algorithms to train agents in Unity environments.

The `mlagents` Python package contains two components: a low level API which
allows you to interact directly with a Unity Environment (`mlagents.envs`) and
an entry point to train (`mlagents-learn`) which allows you to train agents in
Unity Environments using our implementations of reinforcement learning or
imitation learning.

## mlagents.envs

The ML-Agents Toolkit provides a Python API for controlling the Agent simulation
loop of an environment or game built with Unity. This API is used by the
training algorithms inside the ML-Agent Toolkit, but you can also write your own
Python programs using this API. Go [here](../notebooks/getting-started.ipynb)
for a Jupyter Notebook walking through the functionality of the API.

The key objects in the Python API include:

- **UnityEnvironment** — the main interface between the Unity application and
  your code. Use UnityEnvironment to start and control a simulation or training
  session.
- **BrainInfo** — contains all the data from Agents in the simulation, such as
  observations and rewards.
- **BrainParameters** — describes the data elements in a BrainInfo object. For
  example, provides the array length of an observation in BrainInfo.

These classes are all defined in the `ml-agents/mlagents/envs` folder of
the ML-Agents SDK.

To communicate with an Agent in a Unity environment from a Python program, the
Agent must use a LearningBrain.
Your code is expected to return
actions for Agents with LearningBrains.

_Notice: Currently communication between Unity and Python takes place over an
open socket without authentication. As such, please make sure that the network
where training takes place is secure. This will be addressed in a future
release._

### Loading a Unity Environment

Python-side communication happens through `UnityEnvironment` which is located in
`ml-agents/mlagents/envs`. To load a Unity environment from a built binary
file, put the file in the same directory as `envs`. For example, if the filename
of your Unity environment is 3DBall.app, in python, run:

```python
from mlagents.envs.environment import UnityEnvironment
env = UnityEnvironment(file_name="3DBall", worker_id=0, seed=1)
```

- `file_name` is the name of the environment binary (located in the root
  directory of the python project).
- `worker_id` indicates which port to use for communication with the
  environment. For use in parallel training regimes such as A3C.
- `seed` indicates the seed to use when generating random numbers during the
  training process. In environments which do not involve physics calculations,
  setting the seed enables reproducible experimentation by ensuring that the
  environment and trainers utilize the same random seed.

If you want to directly interact with the Editor, you need to use
`file_name=None`, then press the :arrow_forward: button in the Editor when the
message _"Start training by pressing the Play button in the Unity Editor"_ is
displayed on the screen

### Interacting with a Unity Environment

A BrainInfo object contains the following fields:

- **`visual_observations`** : A list of 4 dimensional numpy arrays. Matrix n of
  the list corresponds to the n<sup>th</sup> observation of the Brain.
- **`vector_observations`** : A two dimensional numpy array of dimension `(batch
  size, vector observation size)`.
- **`rewards`** : A list as long as the number of Agents using the Brain
  containing the rewards they each obtained at the previous step.
- **`local_done`** : A list as long as the number of Agents using the Brain
  containing  `done` flags (whether or not the Agent is done).
- **`max_reached`** : A list as long as the number of Agents using the Brain
  containing true if the Agents reached their max steps.
- **`agents`** : A list of the unique ids of the Agents using the Brain.

Once loaded, you can use your UnityEnvironment object, which referenced by a
variable named `env` in this example, can be used in the following way:

- **Print : `print(str(env))`**
  Prints all parameters relevant to the loaded environment and the
  Brains.
- **Reset : `env.reset()`**
  Send a reset signal to the environment, and provides a dictionary mapping
  Brain names to BrainInfo objects.
- **Step : `env.step(action)`**
  Sends a step signal to the environment using the actions. For each Brain :
  - `action` can be one dimensional arrays or two dimensional arrays if you have
    multiple Agents per Brain.

    Returns a dictionary mapping Brain names to BrainInfo objects.

    For example, to access the BrainInfo belonging to a Brain called
    'brain_name', and the BrainInfo field 'vector_observations':

    ```python
    info = env.step()
    brainInfo = info['brain_name']
    observations = brainInfo.vector_observations
    ```

    Note that if you have more than one LearningBrain in the scene, you
    must provide dictionaries from Brain names to arrays for `action`, `memory`
    and `value`. For example: If you have two Learning Brains named `brain1` and
    `brain2` each with one Agent taking two continuous actions, then you can
    have:

    ```python
    action = {'brain1':[1.0, 2.0], 'brain2':[3.0,4.0]}
    ```

    Returns a dictionary mapping Brain names to BrainInfo objects.
- **Close : `env.close()`**
  Sends a shutdown signal to the environment and closes the communication
  socket.

### Modifying the environment from Python
The Environment can be modified by using side channels to send data to the
environment. When creating the environment, pass a list of side channels as
`side_channels` argument to the constructor.

__Note__ : A side channel will only send/receive messages when `env.step` is
called.

#### EngineConfigurationChannel
An `EngineConfiguration` will allow you to modify the time scale and graphics quality of the Unity engine.
`EngineConfigurationChannel` has two methods :

 * `set_configuration_parameters` with arguments
   * width: Defines the width of the display. Default 80.
   * height: Defines the height of the display. Default 80.
   * quality_level: Defines the quality level of the simulation. Default 1.
   * time_scale: Defines the multiplier for the deltatime in the simulation. If set to a higher value, time will pass faster in the simulation but the physics might break. Default 20.
   *  target_frame_rate: Instructs simulation to try to render at a specified frame rate. Default -1.
 * `set_configuration` with argument config which is an `EngineConfig`
 NamedTuple object.

For example :
```python
from mlagents.envs.environment import UnityEnvironment
from mlagents.envs.side_channel.engine_configuration_channel import EngineConfigurationChannel

channel = EngineConfigurationChannel()

env = UnityEnvironment(base_port = 5004, side_channels = [channel])

channel.set_configuration_parameters(time_scale = 2.0)

i = env.reset()
...
```

#### FloatPropertiesChannel
A `FloatPropertiesChannel` will allow you to get and set float properties
in the environment. You can call get_property and set_property on the
side channel to read and write properties.
`FloatPropertiesChannel` has three methods:

 * `set_property` Sets a property in the Unity Environment.
  * key: The string identifier of the property.
  * value: The float value of the property.
 * `get_property` Gets a property in the Unity Environment. If the property was not found, will return None.
  * key: The string identifier of the property.
 * `list_properties` Returns a list of all the string identifiers of the properties

```python
from mlagents.envs.environment import UnityEnvironment
from mlagents.envs.side_channel.float_properties_channel import FloatPropertiesChannel

channel = FloatPropertiesChannel()

env = UnityEnvironment(base_port = 5004, side_channels = [channel])

channel.set_property("parameter_1", 2.0)

i = env.reset()
...
```

Once a property has been modified in Python, you can access it in C# after the next call to `step` as follows:

```csharp
var academy = FindObjectOfType<Academy>();
var sharedProperties = academy.FloatProperties;
float property1 = sharedProperties.GetPropertyWithDefault("parameter_1", 0.0f);
```

## mlagents-learn

For more detailed documentation on using `mlagents-learn`, check out
[Training ML-Agents](Training-ML-Agents.md)
