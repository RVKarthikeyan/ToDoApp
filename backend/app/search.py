from elasticsearch import Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "6XeRw_=V_MX2HffN6gCf"),
    verify_certs=False  # Turn off SSL verification for local dev only
)

def index_task(task_id: int, title: str, desc: str):
    es.index(index="tasks", id=task_id, body={
        "title": title,
        "description": desc
    })

def delete_task(task_id: int):
    es.delete(index="tasks", id=task_id, ignore=[404])

def search_tasks(query: str):
    res = es.search(index="tasks", body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "description"]
            }
        }
    })
    return [int(hit["_id"]) for hit in res["hits"]["hits"]]