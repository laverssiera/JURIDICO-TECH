# Space Law Runtime

Camada de validação jurídica para operações orbitais, lunares, marcianas e de pesquisa extrema.

## Responsabilidades

- Validar conformidade com tratados espaciais.
- Autorizar pesquisa orbital e operações planetárias.
- Registrar risco regulatório em eventos do ecossistema.

## Eventos

- Consome: `archimedes.mars.colony.created`, `research.created`, `research.breakthrough`.
- Publica: `legal.planetary.operation`, `legal.governance.sync`.