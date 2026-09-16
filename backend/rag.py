from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv
import chromadb
import os
import redis
import uuid
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

chroma_client = chromadb.PersistentClient(path="./chroma_data")
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

CACHE_SIMILARITY_THRESHOLD = 0.3  # lower distance = more similar; may need tuning

embedding_function = DefaultEmbeddingFunction()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)


def get_pages_for_span(start, end, page_boundaries):
    pages = [p for (b_start, b_end, p) in page_boundaries if start < b_end and end > b_start]
    if not pages:
        return (1, 1)
    return (min(pages), max(pages))


def build_vector_store(parsed: dict, session_id: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )

    split_docs = splitter.create_documents([parsed["full_text"]])

    doc_texts = []
    doc_metadatas = []

    for doc in split_docs:
        start = doc.metadata.get("start_index", 0)
        end = start + len(doc.page_content)
        page_start, page_end = get_pages_for_span(start, end, parsed["page_boundaries"])
        doc_texts.append(doc.page_content)
        doc_metadatas.append({"page_start": page_start, "page_end": page_end})

    for table in parsed["table_chunks"]:
        doc_texts.append(table["text"])
        doc_metadatas.append({"page_start": table["page"], "page_end": table["page"]})

    collection = chroma_client.create_collection(
        name=session_id,
        embedding_function=embedding_function
    )
    collection.add(
        documents=doc_texts,
        metadatas=doc_metadatas,
        ids=[f"{session_id}_{i}" for i in range(len(doc_texts))]
    )
    return collection


def get_vector_store(session_id: str):
    try:
        collection = chroma_client.get_collection(
            name=session_id,
            embedding_function=embedding_function
        )
        return collection
    except Exception:
        return None


def get_answer(question: str, collection):
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n\n".join(results['documents'][0])

    pages = set()
    for meta in results['metadatas'][0]:
        if meta and "page_start" in meta:
            for p in range(meta["page_start"], meta["page_end"] + 1):
                pages.add(p)
    source_pages = sorted(pages)

    prompt = f"""Answer the question based only on the following context. 
If the answer is not in the context, say "I couldn't find the answer in the uploaded document."

Context:
{context}

Question: {question}

Answer:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content, source_pages


def get_cache_collection(session_id: str):
    try:
        return chroma_client.get_collection(
            name=f"cache_{session_id}",
            embedding_function=embedding_function
        )
    except Exception:
        return chroma_client.create_collection(
            name=f"cache_{session_id}",
            embedding_function=embedding_function
        )


def check_cache(question: str, session_id: str):
    cache_collection = get_cache_collection(session_id)

    if cache_collection.count() == 0:
        return None

    results = cache_collection.query(query_texts=[question], n_results=1)

    if not results['ids'][0]:
        return None

    distance = results['distances'][0][0]

    if distance < CACHE_SIMILARITY_THRESHOLD:
        cached_id = results['ids'][0][0]
        cached = redis_client.get(f"answer:{session_id}:{cached_id}")
        if cached:
            return json.loads(cached)

    return None


def store_in_cache(question: str, answer: str, source_pages: list, session_id: str):
    cache_collection = get_cache_collection(session_id)
    entry_id = str(uuid.uuid4())

    cache_collection.add(documents=[question], ids=[entry_id])
    payload = json.dumps({"answer": answer, "source_pages": source_pages})
    redis_client.set(f"answer:{session_id}:{entry_id}", payload)