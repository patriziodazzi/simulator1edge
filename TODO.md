# TODO - Estensione `simulator1edge` verso Serverless Workflows su Continuum Edge/Cloud

## Visione del Progetto
Costruire un simulatore generico ma realistico per workflow serverless (DAG di funzioni) su continuum edge/cloud, capace di modellare:
- deploy e scheduling SLO-aware;
- gestione stato esternalizzata con consistenza configurabile;
- rete con latenza/bandwidth/contesa;
- semantiche cold/warm start;
- harness sperimentale riproducibile per confrontare politiche e validare contro benchmark empirici.

Obiettivo finale: poter rispondere in modo quantitativo a domande del tipo "quale politica minimizza P99 latency/costo a parità di SLO?".

---

## Stato Avanzamento (aggiornato al 2026-03-04)

### Milestone
- `M1 - MVP Workflow Serverless`: `IN PROGRESS`
  - fatto: `workflow/` con `WorkflowDAG`, validazione aciclicità, execution engine, report di esecuzione;
  - fatto: test `test_workflow_dag.py`, `test_workflow_engine.py`;
  - manca: parser/loader DAG da file (JSON/YAML) e retry semantics complete.
- `M2 - Cold/Warm e Pool`: `IN PROGRESS`
  - fatto: `runtime/` con `ContainerPool`, `ImageCache`, `ServerlessRuntime`, metriche cold/warm e cache;
  - fatto: test `test_runtime_serverless.py` (cold/warm, TTL expiry, eviction, integrazione engine);
  - manca: integrazione completa col layer infrastructure/device e policy di capacity più avanzate.
- `M5 - Scheduling SLO-aware`: `PARTIAL`
  - fatto: framework policy plugin (`policies/`) + catalog factory (`build_placement_policy`, `build_domain_policy`);
  - fatto: baseline placement `first_candidate`, `most_free_memory`, `least_loaded`; domain `sequential`;
  - fatto: test `test_orchestrators.py`, `test_policy_catalog.py`;
  - manca: SLO-aware vero (deadline/costo) e critical-path awareness.
- `M3`, `M4`, `M6`, `M7`, `M8`, `M9`: `NOT STARTED`

### Componenti già introdotti
- `workflow/`: `DONE (scaffold + test)`
- `runtime/`: `DONE (scaffold + test)`
- `policies/`: `DONE (plugin baseline + catalog + test)`
- `state/`, `experiments/`, `benchmarks/`: `TODO`

### Suite test attuale
- `test_workflow_dag.py`: `DONE`
- `test_workflow_engine.py`: `DONE`
- `test_runtime_serverless.py`: `DONE`
- `test_orchestrators.py`: `DONE`
- `test_policy_catalog.py`: `DONE`
- `test_regressions.py`: `DONE`

---

## Milestone Principali

### M1 - MVP Workflow Serverless
- Stato: `IN PROGRESS`
- Nome: `M1 - MVP Workflow Serverless`
- Descrizione: introdurre modello DAG workflow + runtime base di esecuzione funzioni su orchestratori esistenti.
- Priorità: `High`
- Dipendenze: nessuna
- Criterio di completamento (Done):
  - parser/loader DAG funzionante;
  - esecuzione end-to-end di workflow multi-step;
  - metriche base per step e workflow (latency, success/fail, retries).

### M2 - Cold/Warm Start + Container Pool + Image Cache
- Stato: `IN PROGRESS`
- Nome: `M2 - Cold/Warm e Pool`
- Descrizione: modello esplicito di container lifecycle e warm reuse.
- Priorità: `High`
- Dipendenze: `M1`
- Criterio di completamento (Done):
  - supporto cold/warm start parametrico;
  - pool container per device/domain;
  - cache immagini con eviction policy configurabile.

### M3 - Network Model Esteso
- Stato: `NOT STARTED`
- Nome: `M3 - Network Model Esteso`
- Descrizione: latenza, bandwidth, contesa e queueing su link/nodi.
- Priorità: `High`
- Dipendenze: `M1`
- Criterio di completamento (Done):
  - latenza e transfer time dipendenti da payload e path;
  - contesa modellata (code) con effetti su tail latency;
  - test di coerenza su casi sintetici.

### M4 - State Service con Consistency Configurable
- Stato: `NOT STARTED`
- Nome: `M4 - State Service`
- Descrizione: stato esternalizzato per funzioni/workflow con opzioni eventual/bounded/strong.
- Priorità: `High`
- Dipendenze: `M1`, `M3`
- Criterio di completamento (Done):
  - API `read/write` con policy di consistenza configurabile;
  - modellazione costi/latency di sync/replica;
  - scenari che evidenziano differenze tra consistency level.

### M5 - Scheduler Avanzato SLO-aware
- Stato: `PARTIAL`
- Nome: `M5 - Scheduling SLO-aware`
- Descrizione: placement aware di SLO, dominio edge/cloud e critical-path del DAG.
- Priorità: `High`
- Dipendenze: `M1`, `M2`, `M3`, `M4`
- Criterio di completamento (Done):
  - plugin policy per placement/domain/critical-path;
  - almeno 3 baseline confrontabili;
  - supporto vincoli SLO (latency/cost/deadline).

### M6 - Harness Sperimentale Riproducibile
- Stato: `NOT STARTED`
- Nome: `M6 - Experimental Harness`
- Descrizione: framework esperimenti con config scenario, seed, output strutturato.
- Priorità: `High`
- Dipendenze: `M2`, `M3`, `M4`, `M5`
- Criterio di completamento (Done):
  - scenario runner da YAML/JSON;
  - seed riproducibile end-to-end;
  - export CSV/Parquet con schema stabile;
  - comparazione automatica tra politiche baseline.

### M7 - Validazione Empirica
- Stato: `NOT STARTED`
- Nome: `M7 - Empirical Validation`
- Descrizione: calibrazione/validazione con benchmark reali (es. cold start latency).
- Priorità: `Medium`
- Dipendenze: `M2`, `M3`, `M6`
- Criterio di completamento (Done):
  - dataset benchmark referenziato e versionato;
  - errore simulazione vs empirico sotto soglia definita;
  - report di calibrazione ripetibile.

### M8 - CI, QA, Documentazione e Scenari Esempio
- Stato: `NOT STARTED`
- Nome: `M8 - CI & Docs`
- Descrizione: test automation, pipeline CI, guide e scenari pronti.
- Priorità: `High`
- Dipendenze: `M1` (incrementale fino a `M7`)
- Criterio di completamento (Done):
  - CI con unit/integration/regression test;
  - documentazione API/config/policy;
  - esempi completi replicabili.

### M9 - Script Generazione Workload
- Stato: `NOT STARTED`
- Nome: `M9 - Workload Generation`
- Descrizione: generatori di DAG/workload realistici (burst, diurnal, mixed payload).
- Priorità: `Medium`
- Dipendenze: `M1`, `M6`
- Criterio di completamento (Done):
  - script CLI per generare workload parametrico;
  - output validato contro schema scenario;
  - pacchetto benchmark interno pronto all’uso.

---

## Dipendenze tra Milestone (Sintesi)
- `M1` -> base necessaria per tutto.
- `M2`, `M3` partono dopo `M1` in parallelo.
- `M4` richiede `M3` (stato dipende da rete realistica).
- `M5` richiede `M2+M3+M4`.
- `M6` richiede stack completo di modellazione (`M2..M5`).
- `M7` usa `M6` + modelli cold/network.
- `M8` è continua ma completa dopo `M7`.
- `M9` può partire prima, ma pieno valore dopo `M6`.

---

## Features Necessarie (Backlog Funzionale)

### F1 - DAG Workflow Engine
- Nome: `F1 - DAG Engine`
- Descrizione: nodi funzione, archi dipendenza, fan-in/fan-out, retry/failure semantics.
- Priorità: `High`
- Dipendenze: `M1`
- Done: DAG aciclico validato + runtime con scheduler event-driven.

### F2 - Function Runtime Model
- Nome: `F2 - Function Runtime`
- Descrizione: startup, execution, teardown, timeout, memory/CPU footprint.
- Priorità: `High`
- Dipendenze: `M1`, `M2`
- Done: modello parametrico per runtime distributions.

### F3 - Cold/Warm Semantics
- Nome: `F3 - Cold Warm Semantics`
- Descrizione: init cost, TTL warm instance, eviction.
- Priorità: `High`
- Dipendenze: `M2`
- Done: cold/warm ratio misurabile per funzione.

### F4 - State Service
- Nome: `F4 - Externalized State`
- Descrizione: key/value state ops con consistency profile.
- Priorità: `High`
- Dipendenze: `M4`
- Done: letture/scritture con latency model distinto per consistency level.

### F5 - Realistic Network
- Nome: `F5 - Network Realism`
- Descrizione: propagation + serialization + queue delay + bandwidth sharing.
- Priorità: `High`
- Dipendenze: `M3`
- Done: model toggles + stress scenario con contesa.

### F6 - SLO-aware Scheduling
- Nome: `F6 - SLO-aware Scheduling`
- Descrizione: policy aware di deadline, cost, critical path.
- Priorità: `High`
- Dipendenze: `M5`
- Done: policy plugin comparabili su stessi workload.

### F7 - Experiment Harness
- Nome: `F7 - Experiment Harness`
- Descrizione: batch run, sweep parametri, seed control, artifact export.
- Priorità: `High`
- Dipendenze: `M6`
- Done: run replicabile da CLI con manifest scenario.

---

## Requisiti Tecnici e Metriche da Raccogliere

### Requisiti Tecnici
- determinismo con seed fissato;
- separazione netta tra `core simulator` e `policies`;
- schema config versionato;
- output metriche machine-readable;
- performance: supportare campagne multi-run.

### Metriche Minime
- workflow latency: `mean`, `p50`, `p90`, `p95`, `p99`;
- function latency split: `cold_start`, `warm_start`, `execution`, `network`, `state_access`;
- throughput, drop/failure rate, retry count;
- SLO violation rate;
- costo stimato (compute + data transfer + state ops);
- utilizzo risorse edge/cloud;
- queue length e waiting time medi/p99.

---

## Componenti da Sviluppare e Integrare

1. `workflow/`
- parser DAG, validator, runtime DAG executor.

2. `runtime/`
- container pool manager, warm cache manager, cold-start model.

3. `state/`
- state service abstraction + backend simulati + consistency module.

4. `network/` (estensione)
- link contention/queueing, routing-aware transfer, telemetry hooks.

5. `policies/`
- placement/domain/critical-path/SLO policy set + catalog factory.

6. `experiments/`
- scenario loader, runner, sweeper, result aggregator.

7. `benchmarks/`
- dataset benchmark empirici + profili calibrati.

8. `ci/`
- test matrix, lint/type checks, regression suite, artifact upload.

---

## Casi di Test e Scenari di Validazione

### T1 - DAG Correctness
- Nome: `T1 - DAG Correctness`
- Descrizione: validazione topologica, fan-out/fan-in, retries.
- Priorità: `High`
- Dipendenze: `M1`
- Done: suite con DAG sintetici e expected completion order.

### T2 - Cold/Warm Regression
- Nome: `T2 - Cold Warm Regression`
- Descrizione: verifica differenza statisticamente significativa cold vs warm.
- Priorità: `High`
- Dipendenze: `M2`
- Done: test con threshold p95.

### T3 - Network Contention Behavior
- Nome: `T3 - Network Contention`
- Descrizione: aumento load -> aumento queue delay/p99.
- Priorità: `High`
- Dipendenze: `M3`
- Done: trend monotono validato su scenario controllato.

### T4 - Consistency Semantics
- Nome: `T4 - State Consistency`
- Descrizione: eventual vs bounded vs strong su read-after-write.
- Priorità: `High`
- Dipendenze: `M4`
- Done: expected anomaly window rispettata per policy.

### T5 - Policy Comparison Harness
- Nome: `T5 - Policy Comparison`
- Descrizione: confronti baseline su stessi seed/workload.
- Priorità: `High`
- Dipendenze: `M5`, `M6`
- Done: report comparativo auto-generato.

### T6 - Empirical Validation
- Nome: `T6 - Empirical Fit`
- Descrizione: fitting modello vs benchmark reale cold start e network.
- Priorità: `Medium`
- Dipendenze: `M7`
- Done: errore entro range definito (es. MAPE target).

---

## Esempi di Output Attesi / Formati Dati

### Scenario Config (YAML)
```yaml
scenario_id: "wf-edge-cloud-v1"
seed: 42
duration_s: 600
workload:
  type: "dag_trace"
  dag_file: "workloads/etl_small.json"
  arrival:
    model: "poisson"
    rate_per_s: 2.0
infrastructure:
  domains: ["edge-a", "edge-b", "cloud-1"]
  network_profile: "profiles/net_profile_a.yaml"
runtime:
  cold_start:
    enabled: true
    distribution: "lognormal"
  warm_pool:
    ttl_s: 300
policies:
  placement: "most_free_memory"
  domain: "sequential"
state_service:
  consistency: "bounded"
  staleness_ms: 50
output:
  formats: ["csv", "parquet"]
  dir: "results/run_001"
```

### Metrics CSV (esempio colonne)
```text
run_id,scenario_id,seed,policy_placement,policy_domain,workflow_id,completed,latency_ms,p95_ms,p99_ms,slo_violated,cold_starts,warm_starts,state_reads,state_writes,net_bytes,cost_estimate
```

### Run Summary JSON (esempio)
```json
{
  "run_id": "2026-03-04T10:00:00Z_001",
  "scenario_id": "wf-edge-cloud-v1",
  "seed": 42,
  "kpis": {
    "workflow_p99_ms": 820.4,
    "slo_violation_rate": 0.07,
    "cold_start_ratio": 0.31,
    "cost_estimate": 123.45
  },
  "artifacts": {
    "metrics_csv": "results/run_001/metrics.csv",
    "metrics_parquet": "results/run_001/metrics.parquet"
  }
}
```

---

## Piano di Esecuzione Consigliato (Ordine)
1. `M1` + test base DAG.
2. `M2` e `M3` in parallelo.
3. `M4` (state + consistency).
4. `M5` (policy SLO-aware, critical-path).
5. `M6` (harness + export metriche).
6. `M7` (validazione empirica).
7. `M8` + `M9` (industrializzazione e benchmark pack).
