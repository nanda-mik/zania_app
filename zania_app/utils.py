import os
import tempfile
import json

from langchain import hub
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, JSONLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from django.conf import settings

from .exception import ParsingError


def _cleanup_temp_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def process_pdf_document(input_file):
    """
    Processes a PDF file and returns the content of the pages.
    For large PDFs, consider using chunking to load pages in parts.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(input_file.read())
            temp_file_path = temp_file.name
        
        # Load PDF synchronously, for large files switch to async if needed
        loader = PyPDFLoader(temp_file_path)
        pages = loader.load()
    except Exception as e:
        raise ParsingError("Error processing PDF document: " + str(e))
    finally:
        _cleanup_temp_file(temp_file_path)

    return pages


def process_json_document(input_file):
    """
    Processes a JSON file, extracting the 'body' field using jq.
    For large JSON files, async loading and chunking could improve performance.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(input_file.read())
            temp_file_path = temp_file.name
        
        # Load JSON data using jq schema
        loader = JSONLoader(
            file_path=temp_file_path,
            jq_schema='.content[].body',
            text_content=False
        )
        data = loader.load()
    except Exception as e:
        raise ParsingError("Error processing JSON document: " + str(e))
    finally:
        _cleanup_temp_file(temp_file_path)

    return data


def parse_questions_from_file(questions_file):
    """
    Parses a questions JSON file and returns the list of questions.
    """
    file_data = questions_file.read().decode('utf-8')
    questions_json = json.loads(file_data)
    return questions_json.get('questions', [])


def generate_answers_from_documents(documents, questions):
    """
    Given a list of documents and a list of questions, uses a Retrieval-Augmented Generation
    (RAG) approach to generate answers.
    """
    if not documents or not questions:
        raise ParsingError("Documents or questions cannot be empty.")

    try:
        # Initialize OpenAI and Embeddings
        llm = OpenAI(api_key=settings.OPENAI_API_KEY)
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

        # Create a vector store from the documents for question-answer retrieval
        vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever()

        # RAG prompt chain pulled from the hub for simplicity, customize if needed
        prompt = hub.pull("rlm/rag-prompt")
        
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Answer each question and store results in a dictionary
        answers = {}
        for question in questions:
            try:
                result = rag_chain.invoke(question)
                answers[question] = result
            except Exception as e:
                answers[question] = f"Error generating answer: {str(e)}"
    except Exception as e:
        raise ParsingError("Error generating answers from documents: " + str(e))

    return answers
