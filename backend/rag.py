from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv
import chromadb
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

chroma_client = chromadb.Client()
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