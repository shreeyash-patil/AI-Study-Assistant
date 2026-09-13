from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv
import chromadb
import os
import redis
import uuid

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
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

def build_vector_store(chunks: list[str], session_id: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    split_chunks = splitter.create_documents(chunks)
    texts = [doc.page_content for doc in split_chunks]

    collection = chroma_client.create_collection(
        name=session_id,
        embedding_function=embedding_function
    )

    collection.add(
        documents=texts,
        ids=[f"{session_id}_{i}" for i in range(len(texts))]
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

def get_answer(question: str, collection) -> str:
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n\n".join(results['documents'][0])

    prompt = f"""Answer the question based only on the following context. 
            If the answer is not in the context, say "I couldn't find the answer in the uploaded document."

            Context:
            {context}

            Question: {question}

            Answer:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

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
        return redis_client.get(f"answer:{session_id}:{cached_id}")

    return None

def store_in_cache(question: str, answer: str, session_id: str):
    cache_collection = get_cache_collection(session_id)
    entry_id = str(uuid.uuid4())

    cache_collection.add(documents=[question], ids=[entry_id])
    redis_client.set(f"answer:{session_id}:{entry_id}", answer)