
from input_policy import POLICY_GREEDY_BFS, POLICY_GREEDY_DFS
from input_policy import DfsSearchPolicy
from adapter.adapter import InstructionAdapter
from device import Device
from graph.utg import UTG
from utils.logger import Logger
from input_policy import  KeyEvent
class Builder:
    def __init__(self, device:Device, utg:UTG = None, search_method = POLICY_GREEDY_DFS, max_step = 50) -> None:
        self.device = device
        self.utg = utg
        self.max_step = max_step
            
        self.search_policy = DfsSearchPolicy(device, 5, self.utg)
        self.logger = Logger.get_logger(self.__class__.__name__)
    
    def build(self):
        self.logger.info('Start building graph...')
        for i in range(self.max_step):
            if len(self.device.current_state.views) == 0:
                self.logger.debug('No Interactive elements')
                event = KeyEvent(name='BACK')
            else:
                event = self.search_policy.generate_event()
            self.logger.debug(f'Event: {event.to_dict()}')
            self.device.last_event = event
            event.send(self.device)
            self.device.get_current_state()
            if not self.device.is_same_package():
                self.logger.warning('Different App')
                break
            if not isinstance(event, KeyEvent):
                self.utg.add_transition(event, self.device.last_state, self.device.current_state)
            else:
                i -= 1

        self.logger.info('UTG Built...')