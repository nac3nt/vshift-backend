from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Define a schema for nodes and edges
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
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    
    # Create adjacency list
    adjacency_list = {}
    for node in pipeline.nodes:
        adjacency_list[node.id] = []
    
    for edge in pipeline.edges:
        adjacency_list[edge.source].append(edge.target)

    # Check if the graph is a DAG
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
