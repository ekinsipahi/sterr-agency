from django.shortcuts import get_object_or_404, render

from .models import CaseStudy


def case_list(request):
    return render(request, "works/list.html", {"cases": CaseStudy.objects.filter(is_published=True)})


def case_detail(request, slug):
    case = get_object_or_404(CaseStudy.objects.prefetch_related("metrics", "media"), slug=slug, is_published=True)
    others = CaseStudy.objects.filter(is_published=True).exclude(pk=case.pk)[:2]
    return render(request, "works/detail.html", {"case": case, "others": others})
