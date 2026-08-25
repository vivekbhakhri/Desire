"""Admin-only payment / subscription dashboards."""
from __future__ import annotations

import calendar
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractWeek, TruncDay
from django.shortcuts import render

from shop.models import Payment, SubscriptionPayment


def _daily_series(model, value_field, anchor_date):
    """Returns the last 30 days of `value_field` totals ending at `anchor_date`."""
    raw = list(
        model.objects.annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(sum=Sum(value_field))
        .values("day", "sum")
    )
    by_day = {row["day"].date(): row["sum"] for row in raw}
    series = []
    for offset in range(30):
        d = anchor_date - timedelta(days=offset)
        series.append({"day": d, "sum": by_day.get(d.date(), 0)})
    series.reverse()
    return series


def _weekly_series(model, value_field):
    weekly = model.objects.annotate(week_num=ExtractWeek("timestamp")).values(
        "week_num"
    ).annotate(sum=Sum(value_field))
    by_week = {row["week_num"]: row["sum"] for row in weekly}
    return [
        {"week_num": w, "sum": by_week.get(w, 0)}
        for w in range(1, datetime.now().isocalendar()[1] + 1)
    ]


def _monthly_series(model, value_field):
    monthly = model.objects.annotate(month=ExtractMonth("timestamp")).values(
        "month"
    ).annotate(sum=Sum(value_field))
    by_month = {row["month"]: row["sum"] for row in monthly}
    return [
        {"month": calendar.month_name[m], "sum": by_month.get(m, 0)}
        for m in range(1, datetime.now().month + 1)
    ]


def _chart_view(request, model, value_field, template):
    if request.method == "POST":
        anchor = datetime.strptime(request.POST["date"], "%m/%d/%Y")
    else:
        anchor = datetime.today()
    return render(
        request,
        template,
        {
            "day_dataset": _daily_series(model, value_field, anchor),
            "week_dataset": _weekly_series(model, value_field),
            "month_dataset": _monthly_series(model, value_field),
        },
    )


@staff_member_required
def payment_graph_view(request):
    return _chart_view(request, Payment, "amount", "admin/payment_charts.html")


@staff_member_required
def subscription_graph_view(request):
    return _chart_view(
        request, SubscriptionPayment, "price", "admin/subscription_charts.html"
    )
