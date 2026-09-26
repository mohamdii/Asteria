"""Strict date-level historical selection; no estimated publication dates."""
from datetime import date

MAX_AGE_DAYS = {'unemployment': 120, 'vacancies': 240, 'vacancies_bf_supplementary': 240, 'inflation': 730}


def select_observation(observations, country, indicator, cutoff):
    """Input must represent one fixed unit/frequency/adjustment/sector series.

    Each verified row's available_on applies to its exact value/version, not the
    first release of the period or the current dataset update timestamp.
    """
    if not country:
        return {'status': 'missing_country', 'observation': None}
    candidates = []
    for row in observations:
        if row['country'] != country or row['indicator'] != indicator:
            continue
        if row.get('value') is None or not row.get('vintage_verified') or not row.get('evidence_url') or not row.get('vintage_id') or not row.get('available_on'):
            continue
        period_end = date.fromisoformat(row['period_end'])
        available = date.fromisoformat(row['available_on'])
        if available < period_end:
            raise ValueError('Release precedes completed reference period')
        if period_end <= cutoff and available < cutoff:
            candidates.append((period_end, available, row))
    if not candidates:
        return {'status': 'no_verified_historical_match', 'observation': None}
    key = max((p, a) for p, a, _ in candidates)
    matches = [r for p, a, r in candidates if (p, a) == key]
    if len(matches) != 1:
        raise ValueError('Ambiguous historical observation; resolve duplicate versions')
    age = (cutoff-key[0]).days
    if age > MAX_AGE_DAYS[indicator]:
        return {'status': 'stale', 'observation': None, 'age_days': age}
    return {'status': 'matched', 'observation': dict(matches[0]), 'age_days': age}
