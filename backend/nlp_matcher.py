"""
Mathematical NLP Processing logic using TF-IDF and Cosine Similarity.
Calculates how closely a resume matches a target job domain's canonical skill set.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# We map domains to a canonical "ideal" text representation.
# For a real system, this would be scraped job descriptions. Here we use an enriched keyword list.
DOMAIN_CORPUS = {
    "software_engineering": "python java javascript typescript c++ golang rust react node docker kubernetes aws microservices algorithms data structures sql git ci cd agile system design api rest graphql backend frontend full stack",
    "data_science": "python r sql statistics mathematics predictive modeling machine learning deep learning nlp computer vision tensorflow pytorch scikit-learn pandas numpy tableau power bi big data hadoop spark ai",
    "product_management": "product strategy roadmap user research a/b testing data analysis sql agile scrum Jira stakeholder management go-to-market competitive analysis figma wireframing okrs kpis",
    "design": "user experience user interface ux ui product design figma sketch adobe xd photoshop illustrator typography wireframing prototyping usability testing interaction design accessibility heuristics",
    "finance": "excel financial modeling forecasting valuation bloomberg cfa cpa gaap accounting investment banking portfolio management risk analysis financial analysis sql python",
    "marketing": "digital marketing seo sem content strategy google ads social media marketing email marketing copywriting brand management marketing analytics hubspot growth hacking a/b testing conversion rate optimization"
}

def clean_text(text: str) -> str:
    """Basic text cleaning: lowercasing and removing non-alphanumeric chars."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return ' '.join(text.split())

def calculate_resume_match(resume_text: str, domain: str) -> dict:
    """
    Given an uploaded resume and a detected domain, calculates the cosine similarity 
    between the resume and the domain's canonical keyword corpus using TF-IDF.
    """
    if domain not in DOMAIN_CORPUS:
        # Fallback if domain isn't recognized
        return None
        
    canonical_text = DOMAIN_CORPUS[domain]
    cleaned_resume = clean_text(resume_text)
    canonical_set = set(canonical_text.split())
    canonical_terms = list(canonical_set)
    
    # 1. TF-IDF Vectorization
    # We restrict the vocabulary ONLY to the canonical terms. 
    # This acts like an ATS (Applicant Tracking System), filtering out fluff.
    vectorizer = TfidfVectorizer(vocabulary=canonical_terms)
    tfidf_matrix = vectorizer.fit_transform([canonical_text, cleaned_resume])
    
    # 2. Cosine Similarity Calculation
    # tfidf_matrix[0] is the canonical job
    # tfidf_matrix[1] is the user's resume
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Map raw cosine similarity to a readable percentage. 
    percentage_score = min(100, max(0, int(similarity_score * 100))) 
    
    # 3. Extract Overlapping and Missing Keywords
    resume_words = set(cleaned_resume.split())
    
    overlapping = list(canonical_set.intersection(resume_words))
    missing = list(canonical_set.difference(resume_words))
    
    return {
        "domain": domain.replace("_", " ").title(),
        "match_score": percentage_score,
        "overlapping_skills": overlapping[:8], # Show top 8
        "missing_skills": missing[:6]          # Show top 6 missing
    }
