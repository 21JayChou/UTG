import sys
import json
import random
import time
from device import Device
from abc import abstractmethod
from input_event import KeyEvent, InputTextEvent, ScrollEvent
from graph.utg import UTG
from utils.logger import Logger

# Max number of restarts
MAX_NUM_RESTARTS = 5
# Max number of steps outside the app
MAX_NUM_STEPS_OUTSIDE = 5
MAX_NUM_STEPS_OUTSIDE_KILL = 10
# Max number of replay tries
MAX_REPLY_TRIES = 5

# Some input event flags
EVENT_FLAG_STARTED = "+started"
EVENT_FLAG_START_APP = "+start_app"
EVENT_FLAG_STOP_APP = "+stop_app"
EVENT_FLAG_EXPLORE = "+explore"
EVENT_FLAG_NAVIGATE = "+navigate"
EVENT_FLAG_TOUCH = "+touch"

# Policy taxanomy
POLICY_NAIVE_DFS = "dfs_naive"
POLICY_GREEDY_DFS = "dfs_greedy"
POLICY_NAIVE_BFS = "bfs_naive"
POLICY_GREEDY_BFS = "bfs_greedy"
POLICY_REPLAY = "replay"
POLICY_MANUAL = "manual"
POLICY_MONKEY = "monkey"
POLICY_NONE = "none"
POLICY_MEMORY_GUIDED = "memory_guided"  # implemented in input_policy2
POLICY_LLM_GUIDED = "llm_guided"  # implemented in input_policy3



class InputInterruptedException(Exception):
    pass


class InputPolicy(object):
    """
    This class is responsible for generating events to stimulate more app behaviour
    It should call AppEventManager.send_event method continuously
    """

    def __init__(self, device:Device):
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.device = device
        self.action_count = 0

    # def start(self, input_manager):
    #     """
    #     start producing events
    #     :param input_manager: instance of InputManager
    #     """
    #     self.action_count = 0
    #     while input_manager.enabled and self.action_count < input_manager.event_count:
    #         try:
    #             # # make sure the first event is go to HOME screen
    #             # # the second event is to start the app
    #             # if self.action_count == 0 and self.master is None:
    #             #     event = KeyEvent(name="HOME")
    #             # elif self.action_count == 1 and self.master is None:
    #             #     event = IntentEvent(self.app.get_start_intent())
    #             if self.action_count == 0 and self.master is None:
    #                 event = KillAppEvent(app=self.app)
    #             else:
    #                 event = self.generate_event()
    #             input_manager.add_event(event)
    #         except KeyboardInterrupt:
    #             break
    #         except InputInterruptedException as e:
    #             self.logger.warning("stop sending events: %s" % e)
    #             break
    #         # except RuntimeError as e:
    #         #     self.logger.warning(e.message)
    #         #     break
    #         except Exception as e:
    #             self.logger.warning("exception during sending events: %s" % e)
    #             import traceback
    #             traceback.print_exc()
    #             continue
    #         self.action_count += 1

    @abstractmethod
    def generate_event(self):
        """
        generate an event
        @return:
        """
        pass

class DfsSearchPolicy(InputPolicy):
    def __init__(self, device:Device, max_depth, utg:UTG):
        super(DfsSearchPolicy, self).__init__(device)
        self.max_depth = max_depth
        self.event_stack = []
        self.utg = utg

    def generate_event(self):
        if self.device.current_state is None:
            time.sleep(5)
            return KeyEvent(name="BACK")

        current_state = self.device.current_state
        self.logger.info("Current state: %s" % current_state.state_str)
        possible_events = self.device.current_state.get_possible_input()
        self.logger.debug(f'number of possible events: {len(possible_events)}')

        if len(possible_events) == 0:
            return KeyEvent(name="BACK")
        random.shuffle(possible_events)
        for event in possible_events:
            if not self.utg.is_event_explored(event, current_state) and not isinstance(event, InputTextEvent) and not isinstance(event, ScrollEvent):
                return event
        self.logger.debug('State Explored')
        return KeyEvent(name="BACK")




    
    def update_graph(self):
        self.utg.add_transition(self.device.last_event, self.device.last_state, self.device.current_state)