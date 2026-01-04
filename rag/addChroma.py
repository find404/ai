import os, hashlib, chromadb
from Langchain_community.document_loaders import TextLoader, BSHTMLLoader
from Langchain_text_splitters import RecursivecharacterTextsplitter
from datetime import datetime
import chromadb.utils.embedding_functions
from bs4 import Beautifulsoup
from Langchain_core.documents import Document

client = chromadb.Persistentclient(path="/mnt/chromadb-data")
print(client.heartbeat())

collection = client.get_or_create_collection(
    name="db1",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(
        api_key="123456",
        api_base="http://127.0.0.1:11000/v1",
        api_type="OpenAI",
        model_names="Qwen3-Embedding-8B",
    ),
    metadata={
        "description": "my first Chroma collection",
        "created": str(datetime.now())
    }
)


def md5_hash(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()


def load_and_split_html(file_path):
    loader = BSHTMLLoader(file_path)
    documents = loader.load()
    clean_docs = []
    for d in documents:
        soup = BeautifulSoup(d.page_content, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
            tag.decompose()
        body = soup.body
        text = body.get_text(separator="\n") if body else soup.get_text(separator="\n")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        cleaned = "\n".join(lines)
        clean_docs.append(Document(page_content=cleaned, metadata=d.metadata))

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=10, separators=["\n\n", "\n", " ", ""])
    split_docs = text_splitter.split_documents(clean_docs)
    return split_docs


def load_documents(directory):
    result = ""
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith('.html'):
                text_chunks_result = load_and_split_html(filepath)
                result = addChroma(text_chunks_result)
    return result


def addChroma(text_chunks):
    filtered = [d for d in text_chunks if getattr(d, "page_content", None) and d.page_content.strip()]
    documents = [d.page_content for d in filtered]
    metadatas = [d.metadata for d in filtered]
    ids = [f"{md5_hash(metadatas[i].get('source', 'doc'))}-{i}" for i in range(len(filtered))]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    return True


if __name__ == "__main__":
    load_documents("/mnt/files/")
