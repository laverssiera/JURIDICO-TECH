from fastapi import APIRouter, HTTPException

from app.legal_core.legal_knowledge_graph import LegalKnowledgeGraphDomain

router = APIRouter()
_graph = LegalKnowledgeGraphDomain()


@router.post("/nodes")
def add_node(payload: dict) -> dict:
    try:
        return _graph.add_node(payload["node_id"], payload["node_type"], payload.get("attributes"))
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Campo obrigatório: {e}")


@router.post("/edges")
def add_edge(payload: dict) -> dict:
    try:
        return _graph.add_edge(
            source_id=payload["source_id"],
            target_id=payload["target_id"],
            relation=payload["relation"],
            weight=float(payload.get("weight", 1.0)),
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/neighbors/{node_id}")
def neighbors(node_id: str) -> dict:
    return {"neighbors": _graph.neighbors(node_id)}


@router.get("/risk/concentration")
def concentration(node_type: str, threshold: int = 5) -> dict:
    return _graph.detect_concentration_risk(node_type, threshold)


@router.get("/stats")
def graph_stats() -> dict:
    return _graph.graph_stats()
