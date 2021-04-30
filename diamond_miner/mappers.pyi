from diamond_miner.typing import FlowMapper

class SequentialFlowMapper(FlowMapper):
    def __init__(self, prefix_size: int = ...): ...

class IntervalFlowMapper(FlowMapper):
    def __init__(self, prefix_size: int = ..., step: int = ...): ...

class ReverseByteFlowMapper(FlowMapper): ...

class RandomFlowMapper(FlowMapper):
    def __init__(self, seed: int, prefix_size: int = ...): ...