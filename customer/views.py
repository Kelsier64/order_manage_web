from django.shortcuts import render,HttpResponse, redirect
from base.models import Product,Order,ExtendedUser,Announcement
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from .forms import OrderForm
from django.forms import formset_factory
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import requests


class OrderView(LoginRequiredMixin, TemplateView):
    template_name = 'order.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        platforms = Product.objects.values_list('platform', flat=True).distinct()
        product = Product.objects.all()
        OrderFormSet = formset_factory(OrderForm, extra=len(Product.objects.all()))
        formset_instance = OrderFormSet()
        combined = zip(formset_instance.forms,product)
        context['platforms'] = platforms
        context['formset'] = OrderFormSet
        context['combined'] = combined
        return context
    
    def post(self, request, *args, **kwargs):
        OrderFormSet = formset_factory(OrderForm, extra=len(Product.objects.all()))
        formset = OrderFormSet(request.POST)
        if formset.is_valid():
            product = Product.objects.all()
            combined = zip(formset.forms,product)

            for form,product in combined:
                quantity = form.cleaned_data.get('quantity')
                if quantity is None or quantity==0:
                    continue
                notes = form.cleaned_data.get("input_notes")
                try:
                    order = Order.objects.create(product=product, notes=notes, quantity=quantity)
                    user = request.user
                    extendUser = ExtendedUser.objects.get(user=user)
                    extendUser.orders.add(order)
                except:
                    print("fucked")
                    return redirect('/customer/order/')

            return redirect('/customer/order/')  # 重定向到訂單頁面
        else:
            print("not valid")
            
        return redirect('/customer/')

class CheckView(LoginRequiredMixin, TemplateView):
    template_name = 'check.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        extendUser = get_object_or_404(ExtendedUser, user=user)
        sameClass = ExtendedUser.objects.filter(user_class=extendUser.user_class)
        orders = Order.objects.filter(user__in=sameClass).distinct()

        context['orders'] = orders
        return context



class HomeView(LoginRequiredMixin, ListView):
    template_name = 'cHome.html'
    model = Announcement
    context_object_name = 'notes'
