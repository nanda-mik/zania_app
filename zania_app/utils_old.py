import os

from langchain import hub
import tempfile
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document


from langchain.text_splitter import CharacterTextSplitter
from pypdf import PdfReader
import json

from django.conf import settings


def process_pdf(pdf_file):
    """
    input: pdf_file = request.FILES.get('document_file')
    Using pypdfLoader i will process the pf and return the document/pages
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_file.read())
        temp_file_path = temp_file.name

    loader = PyPDFLoader(temp_file_path)
    pages = loader.load()
    # pages = []
    # async for page in loader.alazy_load():
    #     pages.append(page)

    os.remove(temp_file_path)
    return pages

def process_questions(questions_file):
    """
    
    """
    file_data = questions_file.read().decode('utf-8')
    questions = json.loads(file_data)
    return questions['questions']

def answer_questions(documents, questions):
    # import pdb;pdb.set_trace()
    llm = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Initialize InMemory Vector Store
    # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # texts = text_splitter.split_text(document)
    # document = Document(id="3", page_content=doc_text)
    # import pdb;pdb.set_trace()
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    # embedded_texts = embeddings.embed_documents([document])
    vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
    # vectorstore.add_documents([document])

    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")

    # You can set your own prompt like this
    # prompt_template ="""
    # You are a question-answering assistant. Use the context provided below to answer the question accurately.
    
    # Context: {context}
    
    # Question: {question}
    
    # Answer:
    # """

    # prompt = PromptTemplate(
    #     input_variables=["context", "question"],  # These variables will be passed
    #     template=prompt_template
    # )

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answers = {}
    for question in questions:
        result = rag_chain.invoke(question)
        answers[question] = result

    return answers
