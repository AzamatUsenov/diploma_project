"""
Recommendation Engine — calculates match score and generates personalized recommendations.

For each user-job pair:
1. match_score: how well user's skills match job requirements (0-100)
2. missing_skills: what skills the user lacks
3. matching_skills: what skills the user already has
4. recommendation: human-readable advice
"""

from .requirement_parser import parse_skills
from .skill_classifier import classify_skill, LEVEL_WEIGHT


def calculate_match(user_skills, job_skills, verified_skills=None):
    """
    Calculate match score between user and job.

    Args:
        user_skills: list of user's skill names (from UserProfile.skills)
        job_skills: list of required skill names (from Job.parsed_skills or parsed on the fly)
        verified_skills: list of verified skill names (passed tests) — get full weight

    Returns:
        dict: {
            'match_score': 73,
            'matching_skills': ['Python', 'Django'],
            'missing_skills': ['Docker', 'AWS'],
            'extra_skills': ['React'],
            'verified_matching': ['Python'],
        }
    """
    if not job_skills:
        return {
            'match_score': 100,
            'matching_skills': [],
            'missing_skills': [],
            'extra_skills': list(user_skills) if user_skills else [],
            'verified_matching': [],
        }

    verified_set = set(s.strip() for s in (verified_skills or []))
    user_set = set(s.strip() for s in (user_skills or []))
    job_set = set(s.strip() for s in job_skills)

    matching = sorted(user_set & job_set)
    missing = sorted(job_set - user_set)
    extra = sorted(user_set - job_set)
    verified_matching = sorted(verified_set & job_set)

    total_weight = 0
    matched_weight = 0
    for skill in job_set:
        weight = LEVEL_WEIGHT.get(classify_skill(skill), 2)
        total_weight += weight
        if skill in user_set:
            if skill in verified_set:
                matched_weight += weight
            else:
                matched_weight += weight * 0.5

    match_score = round((matched_weight / total_weight) * 100) if total_weight > 0 else 100

    return {
        'match_score': match_score,
        'matching_skills': matching,
        'missing_skills': missing,
        'extra_skills': extra,
        'verified_matching': verified_matching,
    }


def generate_recommendation(user_profile, job, analysis=None):
    """
    Generate personalized recommendation for a user-job pair.

    Args:
        user_profile: UserProfile instance
        job: Job instance
        analysis: pre-computed job analysis dict (optional)

    Returns:
        dict: {
            'match_score': 73,
            'matching_skills': [...],
            'missing_skills': [...],
            'can_apply': True/False,
            'recommendation': 'text advice',
            'learning_path': ['Docker basics', 'AWS fundamentals'],
            'confidence': 'high'/'medium'/'low',
        }
    """
    from .job_analyzer import analyze_job

    if analysis is None:
        analysis = analyze_job(job)

    user_skills = user_profile.skills or []
    verified_skills = user_profile.verified_skills or []
    job_skills = analysis['parsed_skills']

    match_result = calculate_match(user_skills, job_skills, verified_skills)
    match_score = match_result['match_score']
    missing = match_result['missing_skills']
    matching = match_result['matching_skills']

    # Determine if user should apply
    user_level_weight = LEVEL_WEIGHT.get(user_profile.level, 1)
    job_level_weight = LEVEL_WEIGHT.get(job.level, 2)

    can_apply = True
    confidence = 'high'
    recommendation_parts = []

    if match_score >= 80:
        recommendation_parts.append("Отличное совпадение! Вы подходите под большинство требований.")
        confidence = 'high'
    elif match_score >= 60:
        recommendation_parts.append("Хорошее совпадение. Не хватает нескольких навыков, но можно подать заявку.")
        confidence = 'medium'
    elif match_score >= 40:
        recommendation_parts.append("Среднее совпадение. Стоит подтянуть навыки перед подачей заявки.")
        confidence = 'medium'
    else:
        recommendation_parts.append("Низкое совпадение. Рекомендуем сначала изучить недостающие технологии.")
        confidence = 'low'
        can_apply = match_score >= 20  # Still possible but unlikely

    # Check for overqualification warning
    if analysis['is_overqualified'] and user_level_weight <= LEVEL_WEIGHT.get(analysis['detected_level'], 2):
        recommendation_parts.append(
            f"Внимание: требования завышены (честность: {analysis['honesty_score']}%). "
            f"Реальный уровень вакансии — {analysis['detected_level']}, не {job.level}."
        )

    # Special encouragement for juniors
    if user_profile.level == 'junior' and analysis['is_overqualified']:
        recommendation_parts.append(
            "Не бойтесь подавать заявку! Многие компании завышают требования. "
            "Покажите мотивацию и готовность учиться."
        )
        can_apply = True

    # Learning path for missing skills
    learning_path = []
    for skill in missing:
        skill_level = classify_skill(skill)
        if skill_level == 'junior':
            learning_path.append(f"{skill} — базовый уровень, можно освоить за 1-2 недели")
        elif skill_level == 'mid':
            learning_path.append(f"{skill} — средний уровень, потребуется 1-3 месяца практики")
        else:
            learning_path.append(f"{skill} — продвинутый уровень, рекомендуем курс или проект")

    return {
        'match_score': match_score,
        'matching_skills': matching,
        'missing_skills': missing,
        'extra_skills': match_result['extra_skills'],
        'can_apply': can_apply,
        'recommendation': ' '.join(recommendation_parts),
        'learning_path': learning_path,
        'confidence': confidence,
    }
