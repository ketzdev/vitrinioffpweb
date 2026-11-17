from django import forms
from .models import *


class ClienteForms(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'


class UsuarioForms(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'tipo_usuario']

    def save(self, commit=True):
        # salva a senha criptografada (sem isso ela ficaria em texto puro no banco)
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class BuscaClienteForms(forms.Form):
    nome = forms.CharField(label='Nome do cliente', max_length=60)



class BuscaCategoriaForms(forms.Form):
    categoria = forms.ChoiceField(label='Categoria', choices=Produto.CATEGORIA_PRODUTOS)


class FaixaPrecoForms(forms.Form):
    valor_min = forms.DecimalField(label='Valor mínimo', min_value=0, decimal_places=2)
    valor_max = forms.DecimalField(label='Valor máximo', min_value=0, decimal_places=2)

    def clean(self):
        dados = super().clean()
        minimo, maximo = dados.get('valor_min'), dados.get('valor_max')
        if minimo is not None and maximo is not None and minimo > maximo:
            raise forms.ValidationError('O valor mínimo não pode ser maior que o máximo.')
        return dados



class ProdutoForms(forms.ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'



class BuscaVendasClienteForms(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all().order_by('nome'), label='Cliente')


class PeriodoForms(forms.Form):
    data_inicio = forms.DateField(label='Data inicial', widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label='Data final', widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and inicio > fim:
            raise forms.ValidationError('A data inicial não pode ser maior que a final.')
        return dados



class VendaForms(forms.ModelForm):
    desconto = forms.IntegerField(label='Desconto (%)', min_value=0, max_value=100, initial=0)

    class Meta:
        model = Venda
        fields = ['cliente_cpf', 'data', 'forma_pagamento', 'desconto']  # valor_total é calculado
        widgets = {'data': forms.DateInput(attrs={'type': 'date'})}


class ItemVendaForms(forms.ModelForm):
    class Meta:
        model = Item_Venda
        fields = ['produto', 'quantidade_Item']  # preço unitário vem do produto

    def clean(self):
        dados = super().clean()
        produto = dados.get('produto')
        qtd = dados.get('quantidade_Item')
        if produto and qtd:
            if qtd < 1:
                raise forms.ValidationError('A quantidade deve ser de pelo menos 1.')
            if qtd > produto.quantidade:
                raise forms.ValidationError(
                    f'Estoque insuficiente: há apenas {produto.quantidade} unidade(s) de {produto.nome}.'
                )
        return dados
