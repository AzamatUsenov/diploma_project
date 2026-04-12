"""
Requirement Parser — extracts skills and technologies from job requirement text.

Uses keyword matching against a comprehensive skill dictionary.
Handles common variations: "React.js" / "ReactJS" / "React", "Node" / "Node.js", etc.
"""

import re

# Skill aliases: map variations to canonical name
SKILL_ALIASES = {
    # Python ecosystem
    'python': 'Python', 'python3': 'Python', 'py': 'Python',
    'django': 'Django', 'django rest framework': 'DRF', 'drf': 'DRF',
    'flask': 'Flask', 'fastapi': 'FastAPI', 'fast api': 'FastAPI',
    'celery': 'Celery', 'asyncio': 'Asyncio',
    'pandas': 'Pandas', 'numpy': 'NumPy', 'scipy': 'SciPy',
    'sqlalchemy': 'SQLAlchemy', 'alembic': 'Alembic',
    'pytest': 'Pytest', 'unittest': 'Unittest',

    # JavaScript ecosystem
    'javascript': 'JavaScript', 'js': 'JavaScript', 'ecmascript': 'JavaScript',
    'typescript': 'TypeScript', 'ts': 'TypeScript',
    'react': 'React', 'react.js': 'React', 'reactjs': 'React',
    'vue': 'Vue', 'vue.js': 'Vue', 'vuejs': 'Vue',
    'angular': 'Angular', 'angularjs': 'Angular',
    'next.js': 'Next.js', 'nextjs': 'Next.js', 'next': 'Next.js',
    'node': 'Node.js', 'node.js': 'Node.js', 'nodejs': 'Node.js',
    'express': 'Express', 'express.js': 'Express',
    'jquery': 'jQuery', 'webpack': 'Webpack', 'vite': 'Vite',

    # Java ecosystem
    'java': 'Java', 'spring': 'Spring', 'spring boot': 'Spring Boot',
    'hibernate': 'Hibernate', 'maven': 'Maven', 'gradle': 'Gradle',

    # Other languages
    'go': 'Go', 'golang': 'Go',
    'rust': 'Rust', 'c++': 'C++', 'cpp': 'C++',
    'c#': 'C#', 'csharp': 'C#', '.net': '.NET', 'dotnet': '.NET',
    'php': 'PHP', 'laravel': 'Laravel', 'symfony': 'Symfony',
    'ruby': 'Ruby', 'rails': 'Rails', 'ruby on rails': 'Rails',
    'kotlin': 'Kotlin', 'swift': 'Swift',

    # Databases
    'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL', 'psql': 'PostgreSQL',
    'mysql': 'MySQL', 'mariadb': 'MariaDB',
    'mongodb': 'MongoDB', 'mongo': 'MongoDB',
    'redis': 'Redis', 'elasticsearch': 'Elasticsearch',
    'sqlite': 'SQLite', 'oracle': 'Oracle',
    'sql': 'SQL', 'nosql': 'NoSQL',

    # DevOps & Cloud
    'docker': 'Docker', 'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
    'aws': 'AWS', 'amazon web services': 'AWS',
    'gcp': 'GCP', 'google cloud': 'GCP',
    'azure': 'Azure', 'terraform': 'Terraform',
    'ansible': 'Ansible', 'jenkins': 'Jenkins',
    'ci/cd': 'CI/CD', 'cicd': 'CI/CD',
    'nginx': 'Nginx', 'apache': 'Apache',
    'linux': 'Linux', 'bash': 'Bash', 'shell': 'Shell',

    # Tools & Practices
    'git': 'Git', 'github': 'GitHub', 'gitlab': 'GitLab',
    'jira': 'Jira', 'confluence': 'Confluence',
    'agile': 'Agile', 'scrum': 'Scrum', 'kanban': 'Kanban',
    'rest': 'REST API', 'rest api': 'REST API', 'restful': 'REST API',
    'graphql': 'GraphQL', 'grpc': 'gRPC',
    'microservices': 'Microservices', 'микросервисы': 'Microservices',

    # Frontend
    'html': 'HTML', 'html5': 'HTML',
    'css': 'CSS', 'css3': 'CSS', 'scss': 'SCSS', 'sass': 'SASS',
    'tailwind': 'Tailwind CSS', 'tailwindcss': 'Tailwind CSS',
    'bootstrap': 'Bootstrap', 'material ui': 'Material UI',
    'figma': 'Figma', 'ui/ux': 'UI/UX',

    # Testing
    'jest': 'Jest', 'cypress': 'Cypress', 'selenium': 'Selenium',
    'tdd': 'TDD', 'bdd': 'BDD',
    'unit testing': 'Unit Testing', 'integration testing': 'Integration Testing',

    # Data & ML
    'machine learning': 'Machine Learning', 'ml': 'Machine Learning',
    'deep learning': 'Deep Learning', 'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch', 'keras': 'Keras',
    'data science': 'Data Science', 'big data': 'Big Data',
    'spark': 'Spark', 'hadoop': 'Hadoop', 'kafka': 'Kafka',

    # Mobile
    'android': 'Android', 'ios': 'iOS',
    'react native': 'React Native', 'flutter': 'Flutter',

    # Architecture
    'oop': 'OOP', 'solid': 'SOLID', 'design patterns': 'Design Patterns',
    'паттерны проектирования': 'Design Patterns',
    'system design': 'System Design', 'архитектура': 'Architecture',
}

# Build a reverse lookup: canonical name → set of aliases
_CANONICAL_TO_ALIASES = {}
for alias, canonical in SKILL_ALIASES.items():
    _CANONICAL_TO_ALIASES.setdefault(canonical, set()).add(alias)


def parse_skills(text):
    """
    Extract skills from text using keyword matching.

    Args:
        text: Job requirements/description text

    Returns:
        list of canonical skill names found in text
    """
    if not text:
        return []

    text_lower = text.lower()
    found = set()

    # Sort aliases by length (longest first) to match multi-word phrases first
    sorted_aliases = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)

    for alias in sorted_aliases:
        canonical = SKILL_ALIASES[alias]
        if canonical in found:
            continue

        # Use word boundary matching for short aliases to avoid false positives
        if len(alias) <= 2:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.add(canonical)
        elif alias in text_lower:
            found.add(canonical)

    return sorted(found)


def extract_experience_years(text):
    """
    Extract required years of experience from text.

    Looks for patterns like:
    - "3+ years", "3-5 years", "от 3 лет", "не менее 2 лет"
    - "опыт работы от 3 лет"

    Returns:
        int: required years (0 if not found)
    """
    if not text:
        return 0

    patterns = [
        r'(\d+)\+?\s*(?:years?|лет|года)',
        r'(?:от|не менее|минимум|minimum)\s*(\d+)\s*(?:years?|лет|года)',
        r'(\d+)\s*-\s*\d+\s*(?:years?|лет|года)',
        r'(?:experience|опыт)[\w\s]*?(\d+)',
    ]

    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            years = int(match)
            if years <= 20:  # Sanity check
                max_years = max(max_years, years)

    return max_years
