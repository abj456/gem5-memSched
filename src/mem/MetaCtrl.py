from m5.params import *
from m5.SimObject import SimObject


class MetaCtrl(SimObject):
    type = "MetaCtrl"
    cxx_header = "mem/meta_ctrl.hh"
    cxx_class = "gem5::memory::MetaCtrl"

    # # The memory controller to be used
    # mem_ctrl = Param.SimObject(
    #     None, "The memory controller to be used for the meta controller"
    # )

    # # The number of channels in the memory system
    # num_channels = Param.Unsigned(
    #     1, "Number of channels in the memory system"
    # )

    memCtrls = VectorParam.MemCtrl(
        [],
        "List of memory controllers managed by the meta controller",
    )
