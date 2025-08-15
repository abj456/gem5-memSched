/**
 * @file
 * MetaCtrl declaration
 */


#ifndef __META_CTRL_HH__
#define __META_CTRL_HH__

#include <unordered_map>
#include <vector>

#include "base/statistics.hh"
#include "enums/MemSched.hh"
#include "mem/mem_ctrl.hh"
#include "params/MetaCtrl.hh"
#include "sim/sim_object.hh"

namespace gem5
{

namespace memory
{
/**
 * MetaCtrl is a controller that manages multiple memory controllers
 * and provides a unified interface for memory operations.
 */
class MetaCtrl : public SimObject
{
  public:
    MetaCtrl(const MetaCtrlParams &p);

    // void regStats() override;
    virtual void startup() override;   // called once simulation starts
    void processQuantum();     // event handler

    // per-thread累計服務量
    std::unordered_map<ContextID, double> attainedLocalService;
    std::unordered_map<ContextID, double> attainedGlobalService;

  private:
    EventFunctionWrapper quantumEvent;
    // Tick quantum;
    std::vector<MemCtrl*> ctrls;
    const Tick quantum_cycles =
        static_cast<Tick>(200 * 1e7); // 10M cycles, 200 = 1 / 5Ghz ps(ticks)

    const double decay_factor = 0.875; // alpha factor in ATLAS paper

    struct MetaCtrlStats : public statistics::Group
    {
        MetaCtrlStats(MetaCtrl &metaCtrl);

        void regStats() override;

        MetaCtrl &metaCtrl;


        // Add stats here if needed
        statistics::Vector perContextService;
    };
    MetaCtrlStats stats;
};


} // namespace memory

} // namespace gem5

#endif //__META_CTRL_HH__
