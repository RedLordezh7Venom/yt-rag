import numpy as np 
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

def get_video_id(url):
    return url.split("v=")[1]


video_id = "Gfr50f6ZBvo" # only the ID, not full URL, example
try:

    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])

    transcript = " ".join(chunk["text"] for chunk in transcript_list)
    print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")

#chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])

#embeddings, retriever
from langchain_community.embeddings import SentenceTransformerEmbeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embeddings)
retriever = vector_store.as_retriever()

#augmentation
prompt=PromptTemplate(
    template="""
    You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables = ['context', 'question']
)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=8000,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY")
    # other params...
)


def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text


parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})
parser = StrOutputParser()

main_chain = parallel_chain | prompt | llm | parser
if __name__ =='__main__':
    main_chain.invoke('Can you summarize the entire video with main points')
    user_input = input("Ask AI ")
    print(main_chain.invoke(user_input))


