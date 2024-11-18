from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


async def rag_pipeline(text: str, prompt: str) -> str:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2048, chunk_overlap=200, length_function=len
    )
    chunks = splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]

    embedding_model = OpenAIEmbeddings()
    store = await FAISS.afrom_documents(documents, embedding_model)

    top_chunks = store.similarity_search(prompt, k=5)

    return "\n\n".join([doc.page_content for doc in top_chunks])
