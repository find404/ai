from datetime import datetime
import chromadb.utils.embedding_functions as embedding_functions
import chromadb,requests
from typing import List, Dict, Any

client = chromadb.Persistentclient(path="/mnt/chromadb-data")
print(client.heartbeat())

collection = client.get_or_create_collection(
    name="db1",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(
        api_key="123456",
        api_base="http://127.0.0.1:11000/v1",
        api_type="OpenAI",
        model_name="Qwen3-Embedding-8B"
    ),
    metadata={
        "description":"my first Chroma collection",
        "created": str(datetime.now())
    }
)

def rerank_with_jina(query: str, documents: List[str], url: str ="http://127.0.0.1:11001/v1/rerank",api_key: str= "123456", top_k: int = None) -> List[Dict[str, Any]]:
    payload = {
        "model_name": "Qwen3-reranker-8B",
        "query": query,
        "documents": documents,
        "top_k": len(documents)
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        ranked_results = []
        for items result.get("results", []):
            ranked_results.append({
                "document": document[item['index']],
                "relevance_score": item.get("relevance_score", 0.0)
                "index": item.get("index", 0)
            })
            
        return ranked_results
    except requests.exceptions.RequestException as e:
        print(f"jina Reranker 请求失败: {e}")
        return []
    
def query_and_rerank(collection, query_text: str, n_results: int =10):
    initial_results = collection.query(
        query_text = [query_text],
        n_results = n_results,
        include=["document", "metadatas", "distances"],
    )
    
    documents = initial_results["document"][0] if initial_results["document"] else []
    if not documents:
        print("未查询到相关文档")
        return []
    ranked_documents = rerank_with_jina(
        query=query_text,
        documents=documents,
        top_k=n_results
    )
    
    return ranked_documents

if __name__ == "__main__":
    query_and_rerank(collection, "说明文档的地址是？", 10)
