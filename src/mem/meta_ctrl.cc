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

        // Update the stats for this context
        if (cid < 0) {
            // If cid is negative, it is the virtual hardware context
            // which is used for other hw except processors
            // e.g., prefetcher, mmu, etc.
            size_t tail = stats.perContextService.size() - 1;
            stats.perContextService[tail] = attainedGlobalService[cid];
        } else {
            // Otherwise, it is a specific context
            stats.perContextService[cid] = attainedGlobalService[cid];
        }
    }

    // returns the global service map to the memory controllers
    for (auto& ctrl : ctrls) {
        ctrl->updateGlobalService(attainedGlobalService);
    }

    // Reschedule the quantum event
    schedule(quantumEvent, curTick() + quantum_cycles);
}


MetaCtrl::MetaCtrlStats::MetaCtrlStats(MetaCtrl &_metaCtrl)
    : statistics::Group(&_metaCtrl, "meta_ctrl_stats"),
    metaCtrl(metaCtrl),

    ADD_STAT(perContextService, statistics::units::Count::get(),
        "Per-context attained service")
{
}

void
MetaCtrl::MetaCtrlStats::regStats()
{
    using namespace statistics;

    perContextService.init(metaCtrl.ctrls[0]->system()->threads.size() + 1);
}

} // namespace memory
} // namespace gem5
