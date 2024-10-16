from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .utils import (
    process_pdf_document, process_json_document,
    parse_questions_from_file, generate_answers_from_documents
)
from .exception import FileTypeError, ParsingError


def process_document(document_file):
    """
    Processes the document based on its file type and returns the processed documents.
    Raises FileTypeError if the file type is unsupported.
    """
    if document_file.name.endswith('.pdf'):
        return process_pdf_document(document_file)
    elif document_file.name.endswith('.json'):
        return process_json_document(document_file)
    else:
        raise FileTypeError("Unsupported document type")


@csrf_exempt
def ask_endpoint(request):
    """
    Handles POST requests with question and document files,
    returning answers to the questions based on the provided document.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "POST method required"}, status=405)

    questions_file = request.FILES.get('questions_file')
    document_file = request.FILES.get('document_file')

    if not questions_file or not document_file:
        return JsonResponse({"error": "Missing files"}, status=400)

    try:
        questions = parse_questions_from_file(questions_file)
        documents = process_document(document_file)
        answers = generate_answers_from_documents(documents, questions)

        return JsonResponse({"answers": answers}, status=200)
    except (FileTypeError, ParsingError) as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred: " + str(e)}, status=500)
