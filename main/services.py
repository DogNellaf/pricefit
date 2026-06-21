from decimal import Decimal
from typing import Optional

from .models import Analysis, TargetGroup


def compute_coefficient(
    req_min: Decimal,
    req_max: Decimal,
    grp_min: Optional[Decimal],
    grp_max: Optional[Decimal],
) -> float:
    """
    Jaccard similarity of two price ranges.
    Returns 0.0 when the group has no budget defined or ranges don't overlap.
    """
    if grp_min is None or grp_max is None:
        return 0.0

    r_min = float(req_min)
    r_max = float(req_max)
    g_min = float(grp_min)
    g_max = float(grp_max)

    intersection = max(0.0, min(r_max, g_max) - max(r_min, g_min))
    union = max(r_max, g_max) - min(r_min, g_min)

    return intersection / union if union > 0 else 0.0


def generate_recommendations(request_obj) -> "QuerySet[Analysis]":
    """
    (Re-)generate Analysis records for a Request against all TargetGroups.
    Existing analyses for this request are replaced.
    Returns the new queryset ordered by coefficient descending.
    """
    Analysis.objects.filter(request=request_obj).delete()

    groups = TargetGroup.objects.all()
    bulk = [
        Analysis(
            target_group=group,
            request=request_obj,
            coefficient=compute_coefficient(
                request_obj.min_price,
                request_obj.max_price,
                group.min_budget,
                group.max_budget,
            ),
        )
        for group in groups
    ]
    Analysis.objects.bulk_create(bulk)

    return Analysis.objects.filter(request=request_obj).select_related('target_group')
