from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from .parser import extract_text_from_pdf
from .analyzer import analyze_cv, CVAnalysisResult

router = APIRouter()


@router.post("/analyze", response_model=CVAnalysisResult)
async def analyze_cv_endpoint(
    cv_file: UploadFile = File(..., description="CV in PDF format"),
    job_offer: str = Form(..., description="Job offer description text")
):
    """
    Analyze a CV against a job offer.
    
    - **cv_file**: PDF file of the candidate's CV
    - **job_offer**: Text of the job offer to match against
    """
    # Validate file type
    if cv_file.content_type not in ["application/pdf", "application/octet-stream"]:
        if not cv_file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Read and parse PDF
    file_bytes = await cv_file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")

    cv_text = extract_text_from_pdf(file_bytes)
    if not cv_text:
        raise HTTPException(status_code=422, detail="Could not extract text from the PDF")

    # Validate job offer
    if not job_offer or len(job_offer.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job offer description is too short")

    # Run analysis
    try:
        result = analyze_cv(cv_text, job_offer)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return result
