"""
Skill Classifier — classifies skills by difficulty level (Junior/Mid/Senior).

Each skill has an assigned level based on industry expectations:
- Junior: basic tools every developer should know early
- Mid: intermediate tools requiring 1-3 years of experience
- Senior: advanced tools typically used by experienced engineers
"""

# Skill → level mapping
# Level indicates the minimum expected level to know this skill well
SKILL_LEVELS = {
    # Junior-level skills (fundamentals)
    'HTML': 'junior',
    'CSS': 'junior',
    'JavaScript': 'junior',
    'Python': 'junior',
    'Git': 'junior',
    'SQL': 'junior',
    'Bootstrap': 'junior',
    'jQuery': 'junior',
    'REST API': 'junior',
    'Bash': 'junior',
    'Linux': 'junior',
    'Unit Testing': 'junior',
    'OOP': 'junior',
    'JSON': 'junior',

    # Mid-level skills (frameworks & tools)
    'React': 'mid',
    'Vue': 'mid',
    'Angular': 'mid',
    'Django': 'mid',
    'DRF': 'mid',
    'Flask': 'mid',
    'FastAPI': 'mid',
    'Node.js': 'mid',
    'Express': 'mid',
    'TypeScript': 'mid',
    'PostgreSQL': 'mid',
    'MongoDB': 'mid',
    'Redis': 'mid',
    'Docker': 'mid',
    'CI/CD': 'mid',
    'Agile': 'mid',
    'Scrum': 'mid',
    'SCSS': 'mid',
    'SASS': 'mid',
    'Tailwind CSS': 'mid',
    'Webpack': 'mid',
    'Vite': 'mid',
    'Pytest': 'mid',
    'Jest': 'mid',
    'Celery': 'mid',
    'Next.js': 'mid',
    'GraphQL': 'mid',
    'Material UI': 'mid',
    'Spring': 'mid',
    'Spring Boot': 'mid',
    'Java': 'mid',
    'C#': 'mid',
    '.NET': 'mid',
    'Go': 'mid',
    'PHP': 'mid',
    'Laravel': 'mid',
    'Rails': 'mid',
    'Ruby': 'mid',
    'MySQL': 'mid',
    'SQLite': 'mid',
    'Nginx': 'mid',
    'GitHub': 'mid',
    'GitLab': 'mid',
    'Jira': 'mid',
    'React Native': 'mid',
    'Flutter': 'mid',
    'Android': 'mid',
    'iOS': 'mid',
    'Selenium': 'mid',
    'Integration Testing': 'mid',
    'SOLID': 'mid',
    'Design Patterns': 'mid',
    'Figma': 'mid',
    'UI/UX': 'mid',
    'TDD': 'mid',
    'BDD': 'mid',
    'Kotlin': 'mid',
    'Swift': 'mid',

    # Senior-level skills (architecture & advanced tools)
    'Kubernetes': 'senior',
    'AWS': 'senior',
    'GCP': 'senior',
    'Azure': 'senior',
    'Terraform': 'senior',
    'Ansible': 'senior',
    'Microservices': 'senior',
    'System Design': 'senior',
    'Architecture': 'senior',
    'Elasticsearch': 'senior',
    'Kafka': 'senior',
    'Spark': 'senior',
    'Hadoop': 'senior',
    'Machine Learning': 'senior',
    'Deep Learning': 'senior',
    'TensorFlow': 'senior',
    'PyTorch': 'senior',
    'Big Data': 'senior',
    'gRPC': 'senior',
    'C++': 'senior',
    'Rust': 'senior',
    'Oracle': 'senior',
    'Hibernate': 'senior',
    'SQLAlchemy': 'senior',
    'Asyncio': 'senior',
    'Cypress': 'senior',
    'Jenkins': 'senior',
    'Data Science': 'senior',
}

# Numeric weight for levels
LEVEL_WEIGHT = {
    'junior': 1,
    'mid': 2,
    'senior': 3,
}


def classify_skill(skill_name):
    """
    Get the level of a single skill.

    Returns:
        str: 'junior', 'mid', or 'senior' (defaults to 'mid' for unknown skills)
    """
    return SKILL_LEVELS.get(skill_name, 'mid')


def classify_skills(skills):
    """
    Classify a list of skills and return them grouped by level.

    Args:
        skills: list of canonical skill names

    Returns:
        dict: {'junior': [...], 'mid': [...], 'senior': [...]}
    """
    result = {'junior': [], 'mid': [], 'senior': []}
    for skill in skills:
        level = classify_skill(skill)
        result[level].append(skill)
    return result


def detect_level_from_skills(skills, experience_years=0):
    """
    Detect the real required level based on skills and experience.

    Algorithm:
    1. Calculate weighted average of skill levels
    2. Factor in experience years
    3. Return detected level

    Args:
        skills: list of canonical skill names
        experience_years: required years of experience

    Returns:
        str: 'junior', 'mid', or 'senior'
    """
    if not skills and experience_years == 0:
        return 'junior'

    # Calculate average skill weight
    if skills:
        weights = [LEVEL_WEIGHT.get(classify_skill(s), 2) for s in skills]
        avg_weight = sum(weights) / len(weights)
    else:
        avg_weight = 1.0

    # Factor in experience
    if experience_years >= 5:
        exp_weight = 3.0
    elif experience_years >= 2:
        exp_weight = 2.0
    else:
        exp_weight = 1.0

    # Combined score (60% skills, 40% experience)
    combined = avg_weight * 0.6 + exp_weight * 0.4

    # Also factor in count of senior skills
    senior_count = sum(1 for s in skills if classify_skill(s) == 'senior')
    if senior_count >= 3:
        combined += 0.5

    if combined >= 2.5:
        return 'senior'
    elif combined >= 1.6:
        return 'mid'
    return 'junior'
