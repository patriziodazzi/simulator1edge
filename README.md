# simulator1edge

Cloud/Edge simulator prototype.

## Status

This repository appears to be an older research/prototype codebase.
It can still be executed, but it had no packaging metadata and no dependency list,
which made it fail out-of-the-box.

## Quick start

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
pip install -e .
python test/main.py
```

The demo script builds a multi-cloud continuum and runs a simple deployment simulation.

Note: the repository now includes lightweight local fallbacks for `simpy`, `networkx` and `matplotlib` APIs used by this prototype, so the demo can run even in offline/restricted environments.
