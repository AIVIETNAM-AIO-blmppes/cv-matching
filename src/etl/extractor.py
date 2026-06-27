import spacy
import re
from typing import List

# Load model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = spacy.load("en_core_web_sm")

class SemanticExtractor:
    # 1. Generic words that appear in every CV but aren't skills
    BLACKLIST = {
        'student', 'university', 'research', 'assistant', 'system', 'data', 'course', 
        'world', 'project', 'team', 'experience', 'year', 'member', 'level', 'skill',
        'application', 'center', 'school', 'activities', 'volunteer', 'office', 'award'
    }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Removes PII and common noise before NLP processing."""
        # Remove phone numbers (simplified)
        text = re.sub(r'(\+\d{1,3}[- ]?)?\d{10,}', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove common date patterns (e.g., 8/2024, 2022-2025)
        text = re.sub(r'\d{1,2}/\d{2,4}', '', text)
        text = re.sub(r'\d{4}-\d{4}', '', text)
        return text

    @classmethod
    def extract_nouns(cls, text: str) -> List[str]:
        # 1. Clean the raw text
        text = cls._clean_text(text.lower())
        doc = nlp(text)
        chunks = set()
        
        # 2. Extract using NER and POS
        for ent in doc.ents:
            # Drop obvious noise categories
            if ent.label_ in ['PERSON', 'DATE', 'TIME', 'CARDINAL', 'ORDINAL', 'QUANTITY']:
                continue
            # Keep ORG, PRODUCT, WORK_OF_ART (often contain tech skills)
            if len(ent.text) > 2:
                chunks.add(ent.text.strip())

        # 3. Fallback to Noun Chunks with strict constraints
        for chunk in doc.noun_chunks:
            # Clean punctuation and stop words
            clean = " ".join([t.text for t in chunk if not t.is_stop and not t.is_punct])
            
            # Constraints:
            # - Must not be a digit
            # - Must not be in the blacklist
            # - Must be longer than 2 characters
            if clean and not clean.isdigit() and clean not in cls.BLACKLIST and len(clean) > 2:
                # Handle special tech cases like "c++" or "c#"
                if re.match(r'^[a-z0-9\+\#\s]+$', clean):
                    chunks.add(clean)
                
        return list(chunks)