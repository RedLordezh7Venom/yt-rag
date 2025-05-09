import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_huggingface import SentenceTransformerEmbeddings
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Allow CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://phbmgkggdjicjmdmhjofgdhccocokgmg",  # full extension ID
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory store for video RAG chains
video_chains: Dict[str, dict] = {}

class VideoRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    url: str
    question: str

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url

@app.post("/process_video")
def process_video(req: VideoRequest):
    video_id = get_video_id(req.url)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="No captions available for this video.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever()

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.

        {context}
        Question: {question}
        """,
        input_variables=['context', 'question']
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=8000,
        timeout=None,
        max_retries=2,
        api_key=os.getenv("GROQ_API_KEY")
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

    # Store chain in memory
    video_chains[video_id] = {
        'main_chain': main_chain,
        'transcript': transcript
    }
    return {"status": "processed", "video_id": video_id}

@app.post("/ask_question")
def ask_question(req: QuestionRequest):
    video_id = get_video_id(req.url)
    if video_id not in video_chains:
        raise HTTPException(status_code=404, detail="Video not processed. Please process the video first.")
    main_chain = video_chains[video_id]['main_chain']
    try:
        answer = main_chain.invoke(req.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
