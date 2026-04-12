"""
Job Analyzer — the core analysis engine.

Analyzes a job posting to determine:
1. What skills are actually required (parsed from text)
2. What real level the job demands (detected_level)
3. Whether requirements are inflated (is_overqualified)
4. How honest the job posting is (honesty_score: 0-100)
"""

from .requirement_parser import parse_skills, extract_experience_years
from .skill_classifier import (
    classify_skills,
    detect_level_from_skills,
    LEVEL_WEIGHT,
    classify_skill,
)


def analyze_job(job):
    """
    Full analysis of a job posting.

    Args:
        job: Job model instance

    Returns:
        dict with analysis results:
        {
            'parsed_skills': ['Python', 'Django', ...],
            'skills_by_level': {'junior': [...], 'mid': [...], 'senior': [...]},
            'detected_level': 'mid',
            'is_overqualified': True/False,
            'honesty_score': 75,
            'experience_from_text': 3,
            'overqualification_details': {
                'declared_level': 'junior',
                'detected_level': 'mid',
                'senior_skills_count': 2,
                'senior_skills': ['Kubernetes', 'AWS'],
                'total_skills_count': 8,
                'explanation': '...'
            }
        }
    """
    # Combine description and requirements for analysis
    full_text = f"{job.description}\n{job.requirements_text}"

    # Step 1: Parse skills from text
    parsed_skills = parse_skills(full_text)

    # Also include skills from tech_stack field
    if job.tech_stack:
        for tech in job.tech_stack:
            tech_parsed = parse_skills(tech)
            for skill in tech_parsed:
                if skill not in parsed_skills:
                    parsed_skills.append(skill)
        parsed_skills.sort()

    # Step 2: Classify skills by level
    skills_by_level = classify_skills(parsed_skills)

    # Step 3: Extract experience from text
    experience_from_text = extract_experience_years(full_text)
    experience = max(job.experience_years, experience_from_text)

    # Step 4: Detect real level
    detected_level = detect_level_from_skills(parsed_skills, experience)

    # Step 5: Check for overqualification
    declared_level = job.level
    is_overqualified = LEVEL_WEIGHT.get(detected_level, 2) > LEVEL_WEIGHT.get(declared_level, 2)

    # Step 6: Calculate honesty score
    honesty_score = _calculate_honesty_score(
        declared_level=declared_level,
        detected_level=detected_level,
        parsed_skills=parsed_skills,
        skills_by_level=skills_by_level,
        experience=experience,
    )

    # Step 7: Build explanation
    overqualification_details = _build_overqualification_details(
        declared_level=declared_level,
        detected_level=detected_level,
        skills_by_level=skills_by_level,
        parsed_skills=parsed_skills,
        experience=experience,
    )

    return {
        'parsed_skills': parsed_skills,
        'skills_by_level': skills_by_level,
        'detected_level': detected_level,
        'is_overqualified': is_overqualified,
        'honesty_score': honesty_score,
        'experience_from_text': experience_from_text,
        'overqualification_details': overqualification_details,
    }


def _calculate_honesty_score(declared_level, detected_level, parsed_skills, skills_by_level, experience):
    """
    Calculate honesty score (0-100).

    Factors:
    - Level mismatch penalty: -30 if detected > declared by 1 level, -50 if by 2
    - Senior skills in junior job penalty: -5 per senior skill
    - Too many skills penalty: -2 per skill over 10 (unrealistic expectations)
    - Experience mismatch penalty: -10 per excess year for declared level
    """
    score = 100

    # Level mismatch
    level_diff = LEVEL_WEIGHT.get(detected_level, 2) - LEVEL_WEIGHT.get(declared_level, 2)
    if level_diff == 1:
        score -= 30
    elif level_diff >= 2:
        score -= 50

    # Senior skills in junior position
    if declared_level == 'junior':
        senior_count = len(skills_by_level.get('senior', []))
        score -= senior_count * 5

    # Too many skills (unrealistic expectations)
    total_skills = len(parsed_skills)
    if total_skills > 10:
        score -= (total_skills - 10) * 2

    # Experience mismatch
    expected_max_experience = {'junior': 1, 'mid': 3, 'senior': 7}
    max_exp = expected_max_experience.get(declared_level, 3)
    if experience > max_exp:
        score -= (experience - max_exp) * 10

    return max(0, min(100, score))


def _build_overqualification_details(declared_level, detected_level, skills_by_level, parsed_skills, experience):
    """Build human-readable overqualification explanation."""
    senior_skills = skills_by_level.get('senior', [])
    mid_skills = skills_by_level.get('mid', [])

    explanation_parts = []

    level_diff = LEVEL_WEIGHT.get(detected_level, 2) - LEVEL_WEIGHT.get(declared_level, 2)

    if level_diff > 0:
        explanation_parts.append(
            f"Вакансия заявлена как {declared_level}, но реальные требования соответствуют уровню {detected_level}."
        )

    if senior_skills and declared_level in ('junior', 'mid'):
        explanation_parts.append(
            f"Требуются senior-навыки: {', '.join(senior_skills)}."
        )

    if len(parsed_skills) > 12:
        explanation_parts.append(
            f"Слишком много требований ({len(parsed_skills)} навыков) — нереалистичные ожидания."
        )

    expected_max = {'junior': 1, 'mid': 3, 'senior': 7}
    if experience > expected_max.get(declared_level, 3):
        explanation_parts.append(
            f"Требуется {experience} лет опыта, что не соответствует уровню {declared_level}."
        )

    if not explanation_parts:
        explanation_parts.append("Требования соответствуют заявленному уровню.")

    return {
        'declared_level': declared_level,
        'detected_level': detected_level,
        'senior_skills_count': len(senior_skills),
        'senior_skills': senior_skills,
        'mid_skills': mid_skills,
        'total_skills_count': len(parsed_skills),
        'experience_years': experience,
        'explanation': ' '.join(explanation_parts),
    }
