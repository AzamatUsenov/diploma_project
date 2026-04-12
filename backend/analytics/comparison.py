"""
Job Comparison Engine — side-by-side comparison of 2-4 jobs.

Compares jobs across multiple dimensions:
- Salary range
- Honesty score
- Match score (personalized per user)
- Skill requirements overlap
- Training & mentorship
- Gap analysis (what skills you'd need to learn)
- Final verdict with recommendation
"""

from .job_analyzer import analyze_job
from .recommendation_engine import calculate_match, generate_recommendation
from .skill_classifier import LEVEL_WEIGHT


def compare_jobs(jobs, user_profile=None):
    """
    Compare 2-4 jobs side by side.

    Args:
        jobs: list of Job instances (2-4 items)
        user_profile: UserProfile instance (optional, for personalized comparison)

    Returns:
        dict: {
            'jobs': [
                {
                    'id': 1,
                    'title': 'Python Developer',
                    'company': 'TechCorp',
                    'analysis': {...},
                    'match': {...} or None,
                    'scores': {
                        'salary_score': 80,
                        'honesty_score': 75,
                        'match_score': 73,
                        'training_score': 100,
                        'overall_score': 82,
                    }
                },
                ...
            ],
            'comparison': {
                'best_salary': 1,          # job id with best salary
                'most_honest': 2,          # job id with highest honesty
                'best_match': 1,           # job id with best match (if user provided)
                'common_skills': [...],    # skills required by all jobs
                'unique_skills': {1: [...], 2: [...]},  # skills unique to each job
            },
            'verdict': {
                'winner_id': 1,
                'explanation': '...',
            }
        }
    """
    if len(jobs) < 2:
        return {'error': 'Need at least 2 jobs to compare'}
    if len(jobs) > 4:
        jobs = jobs[:4]

    # Analyze each job
    job_data = []
    for job in jobs:
        analysis = analyze_job(job)

        match_data = None
        if user_profile:
            match_data = generate_recommendation(user_profile, job, analysis)

        # Calculate individual scores
        scores = _calculate_scores(job, analysis, match_data)

        job_data.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'is_remote': job.is_remote,
            'level': job.level,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'training_provided': job.training_provided,
            'experience_years': job.experience_years,
            'tech_stack': job.tech_stack,
            'analysis': {
                'parsed_skills': analysis['parsed_skills'],
                'detected_level': analysis['detected_level'],
                'is_overqualified': analysis['is_overqualified'],
                'honesty_score': analysis['honesty_score'],
                'overqualification_details': analysis['overqualification_details'],
            },
            'match': {
                'match_score': match_data['match_score'],
                'matching_skills': match_data['matching_skills'],
                'missing_skills': match_data['missing_skills'],
                'can_apply': match_data['can_apply'],
                'recommendation': match_data['recommendation'],
                'learning_path': match_data['learning_path'],
            } if match_data else None,
            'scores': scores,
        })

    # Cross-job comparison
    comparison = _build_comparison(job_data)

    # Verdict
    verdict = _generate_verdict(job_data, user_profile)

    return {
        'jobs': job_data,
        'comparison': comparison,
        'verdict': verdict,
    }


def _calculate_scores(job, analysis, match_data):
    """Calculate normalized scores (0-100) for each dimension."""
    # Salary score: based on salary_max (normalized later in comparison)
    salary_score = job.salary_max or job.salary_min or 0

    # Honesty score: directly from analysis
    honesty_score = analysis['honesty_score']

    # Match score: from recommendation engine (or 0 if no user)
    match_score = match_data['match_score'] if match_data else 0

    # Training score: bonus for training/mentorship
    training_score = 100 if job.training_provided else 0

    # Overall: weighted average
    if match_data:
        overall = (
            match_score * 0.35 +
            honesty_score * 0.25 +
            training_score * 0.15 +
            min(salary_score / 10000, 100) * 0.25  # Normalize salary roughly
        )
    else:
        overall = (
            honesty_score * 0.40 +
            training_score * 0.20 +
            min(salary_score / 10000, 100) * 0.40
        )

    return {
        'salary_score': salary_score,
        'honesty_score': honesty_score,
        'match_score': match_score,
        'training_score': training_score,
        'overall_score': round(overall),
    }


def _build_comparison(job_data):
    """Build cross-job comparison metrics."""
    # Best salary
    best_salary_job = max(job_data, key=lambda j: j['scores']['salary_score'])

    # Most honest
    most_honest_job = max(job_data, key=lambda j: j['scores']['honesty_score'])

    # Best match (if available)
    best_match_job = max(job_data, key=lambda j: j['scores']['match_score'])

    # Common skills (required by ALL jobs)
    all_skill_sets = [set(j['analysis']['parsed_skills']) for j in job_data]
    common_skills = sorted(set.intersection(*all_skill_sets)) if all_skill_sets else []

    # Unique skills per job
    unique_skills = {}
    for jd in job_data:
        job_skills = set(jd['analysis']['parsed_skills'])
        other_skills = set()
        for other_jd in job_data:
            if other_jd['id'] != jd['id']:
                other_skills |= set(other_jd['analysis']['parsed_skills'])
        unique_skills[jd['id']] = sorted(job_skills - other_skills)

    return {
        'best_salary': best_salary_job['id'],
        'most_honest': most_honest_job['id'],
        'best_match': best_match_job['id'],
        'common_skills': common_skills,
        'unique_skills': unique_skills,
    }


def _generate_verdict(job_data, user_profile):
    """Generate final verdict and recommendation."""
    # Winner = highest overall score
    winner = max(job_data, key=lambda j: j['scores']['overall_score'])

    parts = []
    parts.append(f"Лучший выбор: {winner['title']} в {winner['company']}.")

    if winner['scores']['match_score'] > 0:
        parts.append(f"Матч: {winner['scores']['match_score']}%.")

    parts.append(f"Честность требований: {winner['scores']['honesty_score']}%.")

    if winner['training_provided']:
        parts.append("Бонус: компания предоставляет обучение.")

    if winner['analysis']['is_overqualified'] and user_profile and user_profile.level == 'junior':
        parts.append(
            "Предупреждение: требования завышены, но не бойтесь подавать заявку!"
        )

    return {
        'winner_id': winner['id'],
        'explanation': ' '.join(parts),
    }
