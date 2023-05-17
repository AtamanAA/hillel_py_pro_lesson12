import datetime
import decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render

from .models import Rate
from .forms import ExchangeForm


class DecimalAsFloatJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


def current_rates(request):
    current_date = datetime.date.today()
    current_rates = Rate.objects.filter(date=current_date).all().values()
    return JsonResponse(
        {"current_rates": list(current_rates)}, encoder=DecimalAsFloatJSONEncoder
    )


def index(request):
    if request.method == "POST":
        form = ExchangeForm(request.POST)
        if form.is_valid():
            currency_value = form.cleaned_data["currency_value"]
            operation = form.cleaned_data["operation"]
            currency = form.cleaned_data["currency"]

            current_date = datetime.date.today()
            current_rates = (
                Rate.objects.exclude(vendor="oschad")
                .exclude(vendor="currency")
                .filter(date=current_date, currency_a=currency)
                .all()
                .values()
            )

            if operation == "sell":
                best_rate = current_rates.order_by("sell").last()
            elif operation == "buy":
                best_rate = current_rates.order_by("buy").first()

            result = best_rate[operation] * currency_value
            context = {
                "form": form,
                "result": result,
                "best_rate_value": best_rate[operation],
                "best_vendor": best_rate["vendor"],
            }
            return render(request, "exchange/index.html", context)
    else:
        form = ExchangeForm()
    return render(request, "exchange/index.html", {"form": form})
