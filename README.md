# simulator1edge

Cloud/Edge simulator prototype per modellare infrastrutture distribuite, reti e deployment di microservizi.

## Panoramica

`simulator1edge` è un progetto sperimentale nato per simulare:
- dispositivi cloud/edge con risorse (storage, memoria, bandwidth)
- network topology tra device e tra cloud
- deploy di microservizi tramite orchestratori

Il repository è stato aggiornato per essere eseguibile anche in ambienti offline/restrittivi.

## Struttura del progetto

- `src/simulator1edge/`: codice principale (application, device, network, orchestrator, infrastructure, resource)
- `test/main.py`: demo end-to-end della simulazione
- `test/test_regressions.py`: regression test principali

## Requisiti

- Python 3.10+

Il progetto include fallback locali minimali per `simpy`, `networkx` e `matplotlib` sotto `src/`, così la demo può funzionare anche senza installare dipendenze esterne.

## Guida rapida all'uso

### 1) Setup ambiente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . --no-build-isolation
```

### 2) Eseguire la demo

```bash
python test/main.py
```

Output atteso: righe con trasferimenti/banda tra device e il tempo finale della simulazione (es. `100`).

### 3) Eseguire i test di regressione

```bash
python -m unittest discover -s test -p 'test_regressions.py' -v
```

## Flusso tipico della simulazione

1. Creazione `Simulation`
2. Definizione immagine e microservizio
3. Costruzione delle risorse cloud e dei device
4. Costruzione del continuum e della topologia di rete
5. Deploy orchestrato dei microservizi
6. Avvio simulazione con `sim.run()`

## Troubleshooting veloce

- **`ModuleNotFoundError`**: esegui il setup in virtualenv e `pip install -e . --no-build-isolation`.
- **Nessun package esterno disponibile**: in questo repo i fallback locali permettono comunque di eseguire la demo.
- **Output grafico placeholder**: in assenza di matplotlib reale, il fallback crea un file segnaposto.

## Stato

Prototipo evolutivo: utile per esperimenti e refactoring, non ancora hardenizzato come prodotto production-grade.


## Placement strategy (nuova funzionalità)

Gli orchestratori di dominio (`CloudOrchestrator`, `EdgeOrchestrator`) ora supportano una strategia di piazzamento configurabile:

- `first_fit` (default): mantiene il comportamento precedente
- `best_fit`: seleziona il device con memoria residua minima dopo il deploy (riduce frammentazione)

Esempio:

```python
from simulator1edge.orchestrator.concrete import CloudOrchestrator, DomainOrchestrator

orch = CloudOrchestrator(devices, network, placement_strategy=DomainOrchestrator.BEST_FIT)
```
