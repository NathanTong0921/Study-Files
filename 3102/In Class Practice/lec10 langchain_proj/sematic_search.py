from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "device": "cpu",
    },
    encode_kwargs={
        "normalize_embeddings": True,
    },
)

REVIEWS_CHROMA_PATH = "chroma_data/"

reviews_vector_db = Chroma(persist_directory=REVIEWS_CHROMA_PATH, embedding_function=embedding_model)

question = """Has anyone complained about communication with the hospital staff?"""

relevant_docs = reviews_vector_db.similarity_search(question, k=3)

print(relevant_docs[0].page_content)
print(relevant_docs[1].page_content)
print(relevant_docs[2].page_content)