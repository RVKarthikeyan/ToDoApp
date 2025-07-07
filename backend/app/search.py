from elasticsearch import Elasticsearch
import os

es = Elasticsearch(
    os.getenv("ELASTIC_URL"),  # Example: "https://my-elasticsearch-project-e77d20.es.ap-southeast-1.aws.elastic.cloud:443"
    api_key=os.getenv("ELASTIC_API_KEY")
)

def index_task(task_id: int, title: str, desc: str):
    es.index(index="todo-search-intern", id=task_id, body={
        "title": title,
        "description": desc
    })

def delete_task(task_id: int):
    es.delete(index="todo-search-intern", id=task_id, ignore=[404])

def search_tasks(query: str):
    res = es.search(index="todo-search-intern", body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "description"]
            }
        }
    })
    return [int(hit["_id"]) for hit in res["hits"]["hits"]]
