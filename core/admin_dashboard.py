from django.shortcuts import render
from order.models import Order
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDay, TruncMonth

def order_dashboard(request):

    # Line Chart: Last 7 Days Sales
    last_week = now() - timedelta(days=7)
    daily_sales = (
        Order.objects.filter(created_at__date__gte=last_week, status="Completed")
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(total=Sum("order_total"))
        .order_by("day")
    )
    
    line_labels = [entry["day"].strftime("%d %b") for entry in daily_sales]
    line_values = [entry["total"] for entry in daily_sales]

    # Bar Chart: Monthly revenue (last 6 months)
    last_6_months = now() - timedelta(days=180)
    monthly_sales = (
        Order.objects.filter(created_at__date__gte=last_6_months, status="Completed")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("order_total"))
        .order_by("month")
    )

    bar_labels = [entry["month"].strftime("%b %Y") for entry in monthly_sales]
    bar_values = [entry["total"] for entry in monthly_sales]

    context = {
        "line_labels": line_labels,
        "line_values": line_values,
        "bar_labels": bar_labels,
        "bar_values": bar_values,
    }

    return render(request, "admin/order_dashboard.html", context)
