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

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .exception import ParsingError


def _load_pdf_pages(file_path):
    """
    Loads pages from a PDF file.

    Args:
        file_path: The path to the PDF file.

    Returns:
        List: A list of pages from the PDF.
    """
    loader = PyPDFLoader(file_path)
    return loader.load()


def _load_json_data(file_path):
    """
    Loads data from a JSON file using a jq schema.

    Args:
        file_path: The path to the JSON file.

    Returns:
        List: The parsed JSON data.
    """
    loader = JSONLoader(
        file_path=file_path,
        jq_schema='.content[].body',
        text_content=False
    )
    return loader.load()


def _split_pages_into_documents(pages, source_path):
    """
    Splits the content of pages into smaller chunks and creates Document objects.

    Args:
        pages: The list of page contents (either PDF pages or JSON data).
        source_path: The source file path for metadata.

    Returns:
        List[Document]: A list of chunked documents with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    documents = []

    for i, page in enumerate(pages):
        chunks = splitter.split_text(page.page_content)
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata={"source": source_path, "page": i}))

    return documents


def _save_temp_file(input_file, suffix):
    """
    Saves an uploaded file as a temporary file.

    Args:
        input_file: The uploaded file.
        suffix: The suffix to use for the temp file.

    Returns:
        str: The path to the saved temporary file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(input_file.read())
        return temp_file.name


def _cleanup_temp_file(temp_file_path):
    """
    Cleans up the temporary file after processing.

    Args:
        temp_file_path: The path to the temporary file to be deleted.
    """
    if temp_file_path:
        try:
            os.remove(temp_file_path)
        except OSError as e:
            print(f"Error deleting temporary file: {e}")


def process_pdf_document(input_file):
    """
    Processes a PDF file and returns the content of the pages.
    For large PDFs, consider using chunking to load pages in parts.
    """
    temp_file_path = None
    try:
        temp_file_path = _save_temp_file(input_file, suffix=".pdf")
        pages = _load_pdf_pages(temp_file_path)
        documents = _split_pages_into_documents(pages, temp_file_path)

    except Exception as e:
        raise ParsingError(f"Error processing PDF document: {str(e)}")
    finally:
        _cleanup_temp_file(temp_file_path)

    return documents


def process_json_document(input_file):
    """
    Processes a JSON file, extracting the 'body' field using jq.
    For large JSON files, async loading and chunking could improve performance.
    """
    temp_file_path = None
    try:
        temp_file_path = _save_temp_file(input_file, suffix=".json")
        data = _load_json_data(temp_file_path)
        documents = _split_pages_into_documents(data, temp_file_path)

    except Exception as e:
        raise ParsingError(f"Error processing JSON document: {str(e)}")
    finally:
        _cleanup_temp_file(temp_file_path)

    return documents


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
        retriever = vectorstore.as_retriever(k=5)

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
