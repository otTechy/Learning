from pypdf import PdfReader
from typing import List

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_key_terms(text: str, n: int = 10) -> List[str]:
    import re
    from collections import Counter
    stopwords = set(['the', 'and', 'to', 'of', 'in', 'a', 'is', 'for', 'on', 'with', 'as', 'by', 'at', 'an', 'be', 'are', 'from', 'that', 'this', 'it', 'or', 'was', 'which', 'has', 'have', 'not', 'but', 'can', 'will', 'if', 'their', 'they', 'we', 'you', 'all', 'any', 'so', 'do', 'no'])
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    most_common = Counter(filtered).most_common(n)
    return [w for w, _ in most_common]
