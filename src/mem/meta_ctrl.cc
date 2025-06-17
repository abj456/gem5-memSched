#include "mem/meta_ctrl.hh"

#include <iostream>

#include "debug/MetaCtrl.hh"

namespace gem5
{
namespace memory
{

MetaCtrl::MetaCtrl(const MetaCtrlParams &p):
    SimObject(p),
    quantumEvent([this] { processQuantum(); }, name()),
    ctrls(p.memCtrls)
{
    DPRINTF(MetaCtrl,
        "Setting up MetaCtrl with %zu controllers\n",
        ctrls.size()
    );

    for (int i = 0; i < ctrls.size(); ++i) {
        // Set the MetaCtrl for each memory controller
        ctrls[i]->setMetaCtrl(this);
    }
}

void MetaCtrl::startup()
{
    // Schedule the first quantum event
    schedule(quantumEvent, quantum_cycles);
}

void MetaCtrl::processQuantum()
{
    // DPRINTF(MetaCtrl,
    //     "Processing quantum for MetaCtrl %s, memCtrls.size = %u\n",
    //     name(),
    //     ctrls.size()
    // );
    // Reset the local service map for this quantum
    attainedLocalService.clear();

    // Iterate through all memory controllers and update their service
    for (auto& ctrl : ctrls) {
        std::unordered_map<ContextID, double>
            ctrlDramLocalService = ctrl->getDramLocalService();
        for (const auto& [cid, service] : ctrlDramLocalService) {
            attainedLocalService[cid] += service;
        }
    }

    // updates the global service map
    for (const auto& [cid, localService] : attainedLocalService) {
        attainedGlobalService[cid] = decay_factor * attainedGlobalService[cid]
                                        + (1 - decay_factor) * localService;
    }

    // returns the global service map to the memory controllers
    for (auto& ctrl : ctrls) {
        ctrl->updateGlobalService(attainedGlobalService);
    }

    // Reschedule the quantum event
    schedule(quantumEvent, curTick() + quantum_cycles);
}



} // namespace memory
} // namespace gem5
