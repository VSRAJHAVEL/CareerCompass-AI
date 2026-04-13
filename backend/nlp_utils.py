"""
NLP utilities: intent classification, keyword extraction, entity detection.
"""

import re
from typing import Optional

# ─── Intent Patterns ─────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "resume": [
        r"\bresume\b", r"\bcv\b", r"\bcurriculum vitae\b",
        r"\bwrite.{0,20}resume\b", r"\bupdate.{0,20}resume\b",
        r"\bformat.{0,20}resume\b", r"\bats\b", r"\bapplicant tracking\b",
    ],
    "interview": [
        r"\binterview\b", r"\bhr round\b", r"\btechnical round\b",
        r"\bbehavioral\b", r"\bstar method\b", r"\bonsite\b",
        r"\bprepare.{0,20}(job|role|position)\b",
    ],
    "salary": [
        r"\bsalary\b", r"\bcompensation\b", r"\bpackage\b", r"\bctc\b",
        r"\bstipend\b", r"\bnegotiat\b", r"\bhike\b", r"\brabout pay\b",
        r"\bhow much.{0,30}(earn|make|paid)\b", r"\bincome\b",
    ],
    "skills": [
        r"\bskill\b", r"\blearn\b", r"\bcertif\b", r"\bcourse\b",
        r"\bupskill\b", r"\bbootcamp\b", r"\btool\b",
        r"\bwhat.{0,20}(need|require|must know)\b",
    ],
    "career_path": [
        r"\bcareer\b", r"\bpath\b", r"\bswitch\b", r"\bpivot\b",
        r"\bchange.{0,15}(field|domain|industry|job)\b",
        r"\bgrowth\b", r"\bprogress\b", r"\bpromotion\b",
        r"\bwhat (job|role|position)\b", r"\bwhich (field|domain)\b",
    ],
    "cover_letter": [
        r"\bcover letter\b", r"\bapplication letter\b",
        r"\bwrite.{0,20}letter\b",
    ],
    "linkedin": [
        r"\blinkedin\b", r"\bprofile\b", r"\bnetwork\b",
        r"\bconnection\b", r"\bheadline\b", r"\babout section\b",
    ],
}

# ─── Domain Patterns ──────────────────────────────────────────────────────────

DOMAIN_PATTERNS = {
    "software_engineering": [
        r"\b(software|backend|frontend|full.?stack|devops|sre|sde|developer|programmer|engineer)\b",
        r"\b(python|javascript|typescript|java|c\+\+|golang|rust|react|node\.?js|django|flask)\b",
        r"\b(docker|kubernetes|aws|azure|gcp|cloud|microservice|api)\b",
    ],
    "data_science": [
        r"\b(data science|machine learning|deep learning|ai|artificial intelligence|nlp|computer vision)\b",
        r"\b(data analyst|data engineer|ml engineer|ai engineer|business intelligence)\b",
        r"\b(tensorflow|pytorch|scikit.?learn|pandas|numpy|tableau|power bi|sql)\b",
        r"\b(model|dataset|training|neural network|llm|gpt)\b",
    ],
    "product_management": [
        r"\b(product manager|pm|associate pm|chief product|cpo)\b",
        r"\b(roadmap|user research|agile|scrum|sprint|backlog|a/b test)\b",
        r"\b(product.{0,10}(management|strategy|thinking))\b",
    ],
    "design": [
        r"\b(ux|ui|user experience|user interface|product designer|graphic designer|motion designer)\b",
        r"\b(figma|adobe xd|sketch|photoshop|illustrator|invision)\b",
        r"\b(wireframe|prototype|usability|accessibility)\b",
    ],
    "finance": [
        r"\b(finance|financial|investment|banking|accounting|audit|tax|cfa|cpa)\b",
        r"\b(financial analyst|investment banker|risk analyst|portfolio manager|trader)\b",
        r"\b(bloomberg|excel modeling|gaap|valuation|equity|debt)\b",
    ],
    "marketing": [
        r"\b(marketing|digital marketing|seo|sem|content|brand|growth|social media)\b",
        r"\b(google ads|meta ads|email marketing|copywriting|hubspot|analytics)\b",
        r"\b(marketer|content strategist|growth hacker|brand manager|cmo)\b",
    ],
}

# ─── Skill Keywords ───────────────────────────────────────────────────────────

KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "swift", "kotlin",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "tableau", "power bi",
    "figma", "photoshop", "illustrator",
    "excel", "financial modeling", "bloomberg",
    "google ads", "seo", "sem", "hubspot",
    "agile", "scrum", "jira", "git", "github",
]

# ─── Main NLP Functions ───────────────────────────────────────────────────────

def classify_intent(message: str) -> Optional[str]:
    """Classify the primary intent of the user's message."""
    message_lower = message.lower()
    
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, message_lower))
        if score > 0:
            scores[intent] = score
    
    if not scores:
        return None
    return max(scores, key=scores.get)


def detect_domain(message: str) -> Optional[str]:
    """Detect the professional domain mentioned in the message."""
    message_lower = message.lower()
    
    scores = {}
    for domain, patterns in DOMAIN_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, message_lower, re.IGNORECASE))
        if score > 0:
            scores[domain] = score
    
    if not scores:
        return None
    return max(scores, key=scores.get)


def extract_skills(message: str) -> list[str]:
    """Extract known skill mentions from the user's message."""
    message_lower = message.lower()
    found = []
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', message_lower):
            found.append(skill)
    return found


def extract_job_titles(message: str) -> list[str]:
    """Extract potential job title mentions using pattern matching."""
    title_patterns = [
        r'\b(software engineer|data scientist|product manager|ux designer|ui designer|'
        r'devops engineer|ml engineer|ai engineer|data analyst|frontend developer|'
        r'backend developer|full stack developer|business analyst|financial analyst|'
        r'digital marketer|content writer|project manager|scrum master)\b',
    ]
    message_lower = message.lower()
    found = []
    for pattern in title_patterns:
        matches = re.findall(pattern, message_lower, re.IGNORECASE)
        found.extend(matches)
    return list(set(found))


def analyze_message(message: str) -> dict:
    """
    Full NLP analysis of a user message.
    Returns intent, domain, skills, and job titles.
    """
    return {
        "intent": classify_intent(message),
        "domain": detect_domain(message),
        "skills": extract_skills(message),
        "job_titles": extract_job_titles(message),
    }
