"""
agents/extract.py
ExtractAgent: PDF clause extraction and filtering.
Wraps Level 1 logic: text cleaning, tokenization, filtering, deduplication.
"""

import re
import string
from typing import List, Tuple, Set
from pathlib import Path

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ExtractAgent:
    """
    Extracts and filters meaningful clauses from PDF regulatory documents.
    
    Pipeline:
    1. Text cleaning (hyphen joining, whitespace normalization)
    2. Sentence tokenization
    3. Noise filtering (obligation detection, references, addresses, etc.)
    4. Duplicate detection (Jaccard similarity)
    
    Output: Clean list of distinct regulatory clauses ready for control generation
    """
    
    # Obligation verbs (high-confidence indicators of policy requirements)
    OBLIGATION_VERBS = re.compile(
        r"\b(must|shall|should|may not|required|advised|prohibited|not permitted|"
        r"never|ensure|maintain|submit|register|allot|settle|issue|appoint|"
        r"nominate|verify|delist|quote|arrange|obtain|provide|restrict|"
        r"comply|adhere|follow|inform)\b",
        re.I,
    )
    
    # RBI circular references (metadata, not policy)
    CIRCULAR_REF = re.compile(r"CO\.DT\.|IDMD\.CDD\.|No\.[A-Z0-9\-/]+\s+dated", re.I)
    
    # Section numbers and ref markers
    SECTION_NUM = re.compile(r"^[\d\s\.\)\(A-Za-z]{0,6}$")
    ROMAN_REF = re.compile(r"^(i{1,4}v?|vi{0,3}|ix|x{1,3})\)", re.I)
    
    # Address block signals
    ADDRESS_SIGS = {
        "telephone", "fax", "@rbi.org.in", "www.",
        "fort , mumbai", "central office building", "shahid bhagat singh",
    }
    
    # Salutations and formalities
    SALUTATION = re.compile(r"^(dear\s+sir|yours\s+faithfully|encl\.|chief\s+general)", re.I)
    
    def __init__(self):
        """Initialize agent with NLTK downloads if available."""
        if NLTK_AVAILABLE:
            for pkg in ("punkt", "punkt_tab", "stopwords"):
                try:
                    nltk.data.find(f'tokenizers/{pkg}')
                except LookupError:
                    nltk.download(pkg, quiet=True)
            self.stop_words = set(stopwords.words("english"))
        else:
            self.stop_words = set()
    
    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract clauses from PDF file.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of cleaned, deduplicated clauses
        
        Raises:
            RuntimeError: If PyPDF2 not installed or PDF invalid
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Read all pages
        reader = PdfReader(pdf_file)
        raw_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                raw_pages.append(text)
        
        if not raw_pages:
            raise ValueError("No text extracted from PDF")
        
        # Join pages and clean
        full_text = self._clean_raw("\n".join(raw_pages))
        
        # Tokenize into sentences
        if not NLTK_AVAILABLE:
            # Fallback: simple sentence splitting
            clauses_raw = re.split(r'[.!?]+\s+', full_text)
        else:
            clauses_raw = sent_tokenize(full_text)
        
        # Filter and deduplicate
        clauses = []
        seen: Set[str] = set()
        
        for clause in clauses_raw:
            clause = self._clean_raw(clause)
            
            if not self.is_meaningful(clause):
                continue
            if self.is_duplicate(clause, seen):
                continue
            
            clauses.append(clause)
            seen.add(clause)
        
        return clauses
    
    def extract_from_text(self, text: str) -> List[str]:
        """Extract clauses from raw text string."""
        full_text = self._clean_raw(text)
        
        if not NLTK_AVAILABLE:
            clauses_raw = re.split(r'[.!?]+\s+', full_text)
        else:
            clauses_raw = sent_tokenize(full_text)
        
        clauses = []
        seen: Set[str] = set()
        
        for clause in clauses_raw:
            clause = self._clean_raw(clause)
            
            if not self.is_meaningful(clause):
                continue
            if self.is_duplicate(clause, seen):
                continue
            
            clauses.append(clause)
            seen.add(clause)
        
        return clauses
    
    # ─────────────────────────────────────────────────────────────────────────
    # TEXT CLEANING
    # ─────────────────────────────────────────────────────────────────────────
    
    def _clean_raw(self, text: str) -> str:
        """Clean raw PDF text."""
        # Rejoin soft-hyphenated words
        text = re.sub(r"-\s*\n\s*", "", text)
        # Normalize spaces
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse blank lines
        text = re.sub(r"\n{2,}", "\n", text)
        # Flatten remaining newlines
        text = re.sub(r"\n", " ", text)
        # Final space cleanup
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()
    
    # ─────────────────────────────────────────────────────────────────────────
    # NOISE FILTERING
    # ─────────────────────────────────────────────────────────────────────────
    
    def is_meaningful(self, clause: str) -> bool:
        """
        Filter non-meaningful text.
        Returns True if clause is likely a regulatory requirement.
        """
        s = clause.strip()
        
        # Too short to be complete requirement
        if len(s) < 45:
            return False
        
        # High proportion of non-ASCII (probably OCR artifact)
        if sum(ord(c) > 127 for c in s) / len(s) > 0.30:
            return False
        
        # Structural markers (section numbers, list indices)
        if self.SECTION_NUM.match(s) or self.ROMAN_REF.match(s):
            return False
        
        # Circular references (metadata)
        if self.CIRCULAR_REF.search(s):
            return False
        
        low = s.lower()
        
        # Address blocks
        if sum(sig in low for sig in self.ADDRESS_SIGS) >= 2:
            return False
        
        # Salutations/closings
        if self.SALUTATION.match(low):
            return False
        
        # Section headings (all caps + short)
        if s.isupper() and len(s.split()) <= 6:
            return False
        
        # Must have obligation verb (otherwise not an enforceable requirement)
        if not self.OBLIGATION_VERBS.search(s):
            return False
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────────
    # DEDUPLICATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def is_duplicate(self, clause: str, seen: Set[str], threshold: float = 0.72) -> bool:
        """
        Check if clause is duplicate using Jaccard similarity.
        
        Args:
            clause: Clause to check
            seen: Set of previously seen (unique) clauses
            threshold: Minimum similarity score to consider duplicate (0-1)
        
        Returns:
            True if similar to any seen clause, False if unique
        """
        if not NLTK_AVAILABLE or not self.stop_words:
            # Fallback: simple substring matching
            clause_lower = clause.lower()
            return any(clause_lower in s.lower() or s.lower() in clause_lower for s in seen)
        
        # Tokenize, remove stop words and punctuation
        toks_new = set(word_tokenize(clause.lower())) - self.stop_words - set(string.punctuation)
        
        for prev in seen:
            toks_prev = set(word_tokenize(prev.lower())) - self.stop_words - set(string.punctuation)
            
            if not toks_new or not toks_prev:
                continue
            
            # Jaccard similarity: |intersection| / |union|
            jaccard = len(toks_new & toks_prev) / len(toks_new | toks_prev)
            if jaccard >= threshold:
                return True  # Duplicate found
        
        return False  # Unique clause
    
    # ─────────────────────────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_extraction_stats(self, pdf_path: str) -> dict:
        """Get statistics about extraction from PDF."""
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not installed")
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        raw_pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                raw_pages.append(text)
        
        full_text = self._clean_raw("\n".join(raw_pages))
        
        if not NLTK_AVAILABLE:
            sentences = re.split(r'[.!?]+\s+', full_text)
        else:
            sentences = sent_tokenize(full_text)
        
        meaningful_count = sum(1 for s in sentences if self.is_meaningful(s))
        
        seen: Set[str] = set()
        unique_count = 0
        for s in sentences:
            s = self._clean_raw(s)
            if self.is_meaningful(s) and not self.is_duplicate(s, seen):
                unique_count += 1
                seen.add(s)
        
        return {
            "total_pages": total_pages,
            "total_sentences": len(sentences),
            "meaningful_sentences": meaningful_count,
            "unique_meaningful_clauses": unique_count,
            "duplicates_removed": meaningful_count - unique_count,
        }
