from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    data: dict

class Edge(BaseModel):
    id: str
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    try:
        num_nodes = len(pipeline.nodes)
        num_edges = len(pipeline.edges)

        if num_nodes == 0 or num_edges == 0:
            raise HTTPException(status_code=400, detail="The pipeline must contain at least one node and one edge.")

        adjacency_list = {}
        for node in pipeline.nodes:
            adjacency_list[node.id] = []

        for edge in pipeline.edges:
            if edge.source not in adjacency_list:
                raise HTTPException(status_code=400, detail=f"Invalid edge: {edge.id}. Source node '{edge.source}' does not exist.")
            if edge.target not in adjacency_list:
                raise HTTPException(status_code=400, detail=f"Invalid edge: {edge.id}. Target node '{edge.target}' does not exist.")
            adjacency_list[edge.source].append(edge.target)

        def is_dag(graph):
            visited = set()
            rec_stack = set()

            def dfs(node):
                if node not in visited:
                    visited.add(node)
                    rec_stack.add(node)

                    for neighbor in graph[node]:
                        if neighbor not in visited and dfs(neighbor):
                            return True
                        elif neighbor in rec_stack:
                            return True

                    rec_stack.remove(node)
                return False

            for node in graph:
                if dfs(node):
                    return False
            return True

        is_dag_result = is_dag(adjacency_list)

        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag_result
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please check the input data.")


