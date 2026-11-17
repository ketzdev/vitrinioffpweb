from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import *


def index(request):
    return render(request, 'index.html')


def CadastraUsuario(request):
    if request.method == 'POST':
        form = UsuarioForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso')
            form = UsuarioForms()
        else:
            messages.error(request, 'Erro ao salvar os dados')
    else:
        form = UsuarioForms()
    return render(request, 'cadastrousuario.html', {'form': form})


def CadastraCliente(request):
    if request.method == 'POST':
        form = ClienteForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso')
            form = ClienteForms()
        else:
            messages.error(request, 'Erro ao cadastrar o cliente')
    else:
        form = ClienteForms()
    return render(request, 'cadastrocliente.html', {'form': form})


def CadastraProduto(request):
    if request.method == 'POST':
        form = ProdutoForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso')
            form = ProdutoForms()
        else:
            messages.error(request, 'Erro ao cadastrar o produto')
    else:
        form = ProdutoForms()
    return render(request, 'cadastroproduto.html', {'form': form})


def _calcula_total(venda, extra=Decimal('0.00')):
    """Soma dos itens (+ extra) com o desconto percentual da venda aplicado."""
    subtotal = sum((i.quantidade_Item * i.preco_unitario for i in venda.Item_vendido.all()), Decimal('0.00'))
    subtotal += extra
    return (subtotal * (100 - Decimal(venda.desconto)) / 100).quantize(Decimal('0.01'))


def CadastraVenda(request):
    if request.method == 'POST':
        form = VendaForms(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.valor_total = Decimal('0.00')
            venda.save()
            messages.success(request, 'Venda registrada! Agora adicione os itens.')
            return redirect('AdicionaItemVenda', venda_id=venda.pk)
        messages.error(request, 'Erro ao registrar a venda')
    else:
        form = VendaForms()
    return render(request, 'cadastrovenda.html', {'form': form})


def AdicionaItemVenda(request, venda_id):
    venda = get_object_or_404(Venda.objects.select_related('cliente_cpf'), pk=venda_id)
    if request.method == 'POST':
        form = ItemVendaForms(request.POST)
        if form.is_valid():
            produto = form.cleaned_data['produto']
            qtd = form.cleaned_data['quantidade_Item']
            novo_total = _calcula_total(venda, extra=qtd * produto.valor)
            if novo_total > Decimal('9999.99'):
                messages.error(request, 'O valor total da venda não pode ultrapassar R$ 9999,99.')
            else:
                with transaction.atomic():
                    item = form.save(commit=False)
                    item.venda = venda
                    item.preco_unitario = produto.valor
                    item.save()
                    Produto.objects.filter(pk=produto.pk).update(quantidade=F('quantidade') - qtd)
                    venda.valor_total = novo_total
                    venda.save(update_fields=['valor_total'])
                messages.success(request, 'Item adicionado à venda.')
                return redirect('AdicionaItemVenda', venda_id=venda.pk)
    else:
        form = ItemVendaForms()
    context = {
        'form': form,
        'venda': venda,
        'itens': venda.Item_vendido.select_related('produto'),
    }
    return render(request, 'adicionaitemvenda.html', context)


#consultas
# listar todos os clientes
def ConsultaClientes(request):
    context = {'clientes': Cliente.objects.all().order_by('nome')}
    return render(request, 'consultaclientes.html', context)


#consultar cliente por nome
def ConsultaClientePorNome(request):
    clientes, buscou = None, False
    form = BuscaClienteForms(request.GET or None)
    if form.is_valid():
        buscou = True
        clientes = Cliente.objects.filter(nome__icontains=form.cleaned_data['nome']).order_by('nome')
    context = {'form': form, 'clientes': clientes, 'buscou': buscou}
    return render(request, 'consultaclientepornome.html', context)


#listar todos os produtos
def ConsultaProdutos(request):
    context = {'produtos': Produto.objects.all().order_by('nome')}
    return render(request, 'consultaprodutos.html', context)


#consultar produtos por categoria
def ConsultaProdutosPorCategoria(request):
    produtos, buscou = None, False
    form = BuscaCategoriaForms(request.GET or None)
    if form.is_valid():
        buscou = True
        produtos = Produto.objects.filter(cat_produto=form.cleaned_data['categoria']).order_by('nome')
    context = {'form': form, 'produtos': produtos, 'buscou': buscou}
    return render(request, 'consultaprodutoscategoria.html', context)


#consultar produtos por faixa de preço
def ConsultaProdutosPorPreco(request):
    produtos, buscou = None, False
    form = FaixaPrecoForms(request.GET or None)
    if form.is_valid():
        buscou = True
        produtos = Produto.objects.filter(
            valor__gte=form.cleaned_data['valor_min'],
            valor__lte=form.cleaned_data['valor_max'],
        ).order_by('valor')
    context = {'form': form, 'produtos': produtos, 'buscou': buscou}
    return render(request, 'consultaprodutosfaixapreco.html', context)


#consultar produtos com estoque baixo (menos de 5 unidades)
def ConsultaEstoqueBaixo(request):
    produtos = Produto.objects.filter(quantidade__lt=5).order_by('quantidade')
    return render(request, 'consultaestoquebaixo.html', {'produtos': produtos})


#listar todas as vendas
def ConsultaVendas(request):
    vendas = Venda.objects.select_related('cliente_cpf').order_by('-data', '-id')
    return render(request, 'consultavendas.html', {'vendas': vendas})


#consultar vendas por cliente
def ConsultaVendasPorCliente(request):
    vendas, buscou, cliente = None, False, None
    form = BuscaVendasClienteForms(request.GET or None)
    if form.is_valid():
        buscou = True
        cliente = form.cleaned_data['cliente']
        vendas = Venda.objects.filter(cliente_cpf=cliente).select_related('cliente_cpf').order_by('-data')
    context = {'form': form, 'vendas': vendas, 'buscou': buscou, 'cliente': cliente}
    return render(request, 'consultavendasporcliente.html', context)


#consultar vendas por período
def ConsultaVendasPorPeriodo(request):
    vendas, buscou = None, False
    form = PeriodoForms(request.GET or None)
    if form.is_valid():
        buscou = True
        vendas = Venda.objects.filter(
            data__range=(form.cleaned_data['data_inicio'], form.cleaned_data['data_fim'])
        ).select_related('cliente_cpf').order_by('data')
    context = {'form': form, 'vendas': vendas, 'buscou': buscou}
    return render(request, 'consultavendasporperiodo.html', context)


#consultar itens de uma venda
def ConsultaItensVenda(request, venda_id):
    venda = get_object_or_404(Venda.objects.select_related('cliente_cpf'), pk=venda_id)
    itens = Item_Venda.objects.filter(venda=venda).select_related('produto').order_by('id')
    return render(request, 'consultaitensvenda.html', {'venda': venda, 'itens': itens})
