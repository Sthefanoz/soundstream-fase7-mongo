"""
Formulario de pago para contratar un plan. Valida la tarjeta en el servidor
(Luhn + fecha de vencimiento + CVV) cuando el metodo es Tarjeta de Credito.
Los datos de tarjeta NO se almacenan: solo se validan (pago simulado).
"""

import re

from django import forms
from django.utils import timezone


def luhn_valido(numero):
    """Algoritmo de Luhn para validar el numero de tarjeta."""
    digitos = [int(d) for d in numero if d.isdigit()]
    if not 13 <= len(digitos) <= 19:
        return False
    suma, par = 0, False
    for d in reversed(digitos):
        if par:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
        par = not par
    return suma % 10 == 0


class ContratarForm(forms.Form):
    METODOS = [
        ('Tarjeta de Crédito', 'Tarjeta de Crédito'),
        ('Paypal', 'Paypal'),
    ]

    metodo_pago = forms.ChoiceField(
        choices=METODOS, label='Metodo de pago',
        widget=forms.Select(attrs={
            'style': 'width:100%; padding:12px; border-radius:10px; '
                     'background:#15151f; color:#fff; border:1px solid #2a2a3a;',
        }))
    numero_tarjeta = forms.CharField(
        label='Numero de tarjeta', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '4242 4242 4242 4242', 'inputmode': 'numeric',
            'maxlength': '19', 'autocomplete': 'cc-number',
        }))
    vence = forms.CharField(
        label='Vence (MM/AA)', required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/AA', 'maxlength': '5'}))
    cvv = forms.CharField(
        label='CVV', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '123', 'inputmode': 'numeric', 'maxlength': '4'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('metodo_pago') == 'Paypal':
            return cleaned  # Paypal no requiere datos de tarjeta

        numero = re.sub(r'[\s-]', '', cleaned.get('numero_tarjeta') or '')
        vence = (cleaned.get('vence') or '').strip()
        cvv = (cleaned.get('cvv') or '').strip()

        if not numero:
            self.add_error('numero_tarjeta', 'Ingresa el numero de tarjeta.')
        elif not numero.isdigit() or not luhn_valido(numero):
            self.add_error('numero_tarjeta', 'Numero de tarjeta invalido.')

        match = re.match(r'^(\d{2})/(\d{2})$', vence)
        if not match:
            self.add_error('vence', 'Usa el formato MM/AA.')
        else:
            mes, anio = int(match.group(1)), 2000 + int(match.group(2))
            if not 1 <= mes <= 12:
                self.add_error('vence', 'Mes invalido.')
            else:
                hoy = timezone.localdate()
                if (anio, mes) < (hoy.year, hoy.month):
                    self.add_error('vence', 'La tarjeta esta vencida.')

        if not (cvv.isdigit() and len(cvv) in (3, 4)):
            self.add_error('cvv', 'CVV invalido (3 o 4 digitos).')

        return cleaned
