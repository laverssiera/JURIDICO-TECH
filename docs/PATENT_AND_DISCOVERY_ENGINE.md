# PATENT AND DISCOVERY ENGINE

## Objetivo
Controlar ciclo de vida de patente e descoberta cientifica: novidade, prior art, aprovacao e licenca.

## APIs
- POST /patents/register
- POST /patents/analyze-novelty
- POST /patents/validate-prior-art
- POST /patents/license
- GET /patents/{id}

## Eventos
- patent.created
- patent.approved
- patent.licensed
- science.discovery.validated
- science.discovery.disputed
