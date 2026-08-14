# **MIGRATION_V1_TO_V2.md**  
### *Portal‑OS Foundation OS → Unified Kernel OS*

---

## **1. Overview**
Portal‑OS v1 is the **Foundation OS**: a subsystem‑based architecture with discrete modules (kernel, runtime, cognitive, TEC, substrate, etc.).

Portal‑OS v2 is the **Unified Kernel OS**: a graph‑driven, mesh‑based, constitutionally governed operating system where all v1 subsystems are unified under a single kernel lattice.

This document explains **how each v1 subsystem evolves into its v2 counterpart**, and how the architecture transitions from *modular* → *unified*.

---

## **2. Core Migration Principles**

### **A. Subsystems become graphs**
V1 modules (runtime, TEC, cognitive, substrate) become **graph engines** in v2.

### **B. Kernel becomes a lattice**
The v1 kernel becomes the **Unified Kernel Lattice**, absorbing scheduling, routing, and state management.

### **C. Cognition becomes a mesh**
The v1 cognitive engine becomes the **Cognitive Mesh**, with agents, domains, and shared memory.

### **D. TEC becomes chains**
V1 TEC pipelines become **TEC Chains**, with chain nodes and chain schedulers.

### **E. Substrate becomes Class‑S**
V1 substrate becomes **Substrate‑S**, with structured channels and integrity layers.

### **F. Umbrella becomes a constitution**
Umbrella v1 becomes **Umbrella v2**, a constitutional governance layer.

### **G. Identity becomes physics**
Identity physics becomes **Identity v2**, with registry + auth + key management.

---

## **3. Migration Map (Subsystem → Unified Kernel OS)**

### **Kernel → Unified Kernel**
- v1 kernel  
- v1 scheduler  
- v1 signals  
- v1 process manager  

**Become:**  
- unified_kernel/kernel_unification_layer  
- unified_kernel/kernel_graph  
- unified_kernel/kernel_channels  
- unified_kernel/kernel_state  

---

### **Runtime → Runtime Graph**
- v1 runtime engine  
- v1 event bus  
- v1 routing  

**Become:**  
- runtime_graph/graph_engine  
- runtime_graph/graph_scheduler  
- runtime_graph/graph_nodes  
- runtime_graph/graph_events  

---

### **Cognitive Engine → Cognitive Mesh**
- v1 cognitive engine  
- v1 memory manager  
- v1 suites  

**Become:**  
- cognitive_mesh/mesh_engine  
- cognitive_mesh/mesh_agents  
- cognitive_mesh/mesh_memory  
- cognitive_mesh/mesh_domains  

---

### **TEC Pipelines → TEC Chains**
- v1 TEC pipelines  
- v1 TEC scheduler  

**Become:**  
- tec_chains/chain_engine  
- tec_chains/chain_nodes  
- tec_chains/chain_scheduler  
- tec_chains/chain_domains  

---

### **Substrate Class‑C → Substrate Class‑S**
- v1 substrate  
- v1 network stack  
- v1 fs  

**Become:**  
- substrate_s/class_s  
- substrate_s/substrate_memory  
- substrate_s/substrate_integrity  
- substrate_s/substrate_channels  

---

### **Umbrella v1 → Umbrella v2**
- v1 umbrella  
- v1 governance rules  

**Become:**  
- governance/constitution  
- governance/governance_chambers  
- governance/governance_graph  
- governance/voting_engine  
- governance/rules_engine  
- umbrella_v2/integration  

---

### **Identity (basic) → Identity v2 (physics)**
- v1 identity (implicit)  

**Become:**  
- identity/auth_engine  
- identity/identity_registry  
- identity/key_management  
- identity/credential_store  

---

### **Security (basic) → Security v2**
- v1 basic security  

**Become:**  
- security/crypto_engine  
- security/access_control  
- security/domain_isolation  
- security/audit_log  

---

## **4. Architectural Shifts**

### **From Modules → Meshes**
V1 is subsystem‑based.  
V2 is mesh‑based.

### **From Pipelines → Chains**
V1 TEC pipelines are linear.  
V2 TEC chains are multi‑node and multi‑domain.

### **From Events → Graphs**
V1 runtime dispatches events.  
V2 runtime is a graph engine.

### **From Rules → Constitution**
V1 Umbrella enforces rules.  
V2 Umbrella defines constitutional invariants.

### **From Identity → Physics**
Identity becomes a physics layer with registry + keys + credentials.

---

## **5. Migration Strategy**

### **Step 1 — Freeze v1**
No structural changes to portal-os-v1.

### **Step 2 — Build v2 clean**
portal-os-v2 is a **clean repo**, importing v1 concepts but not v1 code.

### **Step 3 — Map v1 subsystems to v2 equivalents**
Use the migration map above.

### **Step 4 — Implement Unified Kernel first**
All other v2 systems depend on it.

### **Step 5 — Integrate Umbrella v2**
Governance becomes constitutional.

### **Step 6 — Expand into v3 (World OS)**
Once v2 is stable, v3 builds on top.

---

## **6. Version Boundaries**

### **v1**  
Foundation OS  
Subsystem architecture  
Local scale  

### **v2**  
Unified Kernel OS  
Graph + mesh + chain architecture  
Multi‑domain scale  

### **v3**  
World OS  
Planetary substrate  
Global scale  

---

## **7. Data Flow Migration**

### **V1 Linear Flow**
```
Request → Kernel → Runtime → Cognitive → TEC → Substrate → Response
```

### **V2 Graph Flow**
```
Request → Identity Check → Governance Validation → Unified Kernel Lattice
    ↓
    Runtime Graph Engine (all tasks as DAG nodes)
    ↓
    Cognitive Mesh (multi-agent reasoning)
    ↓
    TEC Chains (consensus-based execution)
    ↓
    Substrate-S (distributed resources)
    ↓
    Umbrella v2 Policy Engine (rule enforcement)
    ↓
Response
```

---

## **8. Integration Points**

### **Unified Kernel ↔ Umbrella v2**
The unified kernel enforces constitutional rules from Umbrella v2.

### **Runtime Graph ↔ Cognitive Mesh**
Graph nodes can invoke cognitive agents for reasoning.

### **TEC Chains ↔ Orchestration**
Chains participate in global consensus via orchestration layer.

### **Substrate-S ↔ All Systems**
All systems allocate resources through Substrate-S channels.

---

## **9. Compatibility & Versioning**

### **API Compatibility**
V2 APIs are **not backward compatible** with V1.  
V1 systems remain frozen in portal-os-v1/.  
V2 is a clean evolution, not a patch.

### **Data Migration**
V1 state can be exported and re-imported into V2 (application-dependent).  
No automatic migration tool provided.

---

## **10. Deployment Timeline**

| Phase | Duration | Milestone |
|-------|----------|-----------|
| V1 Stable | ✓ Complete | Foundation OS production-ready |
| V2 Development | In Progress | Unified Kernel implementation |
| V2 Alpha Testing | Planned | Internal domain testing |
| V2 Beta | Planned | Multi-domain federation |
| V2 GA | Planned | Production deployment |
| V3 Development | Future | World OS implementation |

---

## **11. Next Documents**

- **MIGRATION_V2_TO_V3.md** — Unified Kernel → World OS evolution
- **V1_API_REFERENCE.md** — Foundation OS endpoint documentation
- **V2_IMPLEMENTATION_GUIDE.md** — Code skeleton and examples
- **V3_ARCHITECTURE_DEEP_DIVE.md** — Planetary-scale consensus

---

## **12. Status**
✅ Portal‑OS v1 is complete (portal-os-v1/)  
✅ Portal‑OS v2 repo structure is complete (portal-os-v2/)  
✅ Portal‑OS v3 repo structure is complete (portal-os-v3/)  
✅ Portal‑OS deploy layer is complete (portal-os-deploy/)  
✅ Migration path is now fully documented (this file)

---

**Ready to proceed with V2 implementation or next migration document.**
