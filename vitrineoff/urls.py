from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from venda.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),

    # cadastros
    path('CadastraUsuario/', CadastraUsuario, name='CadastraUsuario'),
    path('CadastraCliente/', CadastraCliente, name='CadastraCliente'),
    path('CadastraProduto/', CadastraProduto, name='CadastraProduto'),
    path('CadastraVenda/', CadastraVenda, name='CadastraVenda'),
    path('AdicionaItemVenda/<int:venda_id>/', AdicionaItemVenda, name='AdicionaItemVenda'),

    #consultas
    path('ConsultaClientes/', ConsultaClientes, name='ConsultaClientes'),                    
    path('ConsultaClientePorNome/', ConsultaClientePorNome, name='ConsultaClientePorNome'),  
    path('ConsultaProdutos/', ConsultaProdutos, name='ConsultaProdutos'),                                
    path('ConsultaProdutosPorCategoria/', ConsultaProdutosPorCategoria, name='ConsultaProdutosPorCategoria'),  
    path('ConsultaProdutosPorPreco/', ConsultaProdutosPorPreco, name='ConsultaProdutosPorPreco'),        
    path('ConsultaEstoqueBaixo/', ConsultaEstoqueBaixo, name='ConsultaEstoqueBaixo'),                    
    path('ConsultaVendas/', ConsultaVendas, name='ConsultaVendas'),                                     
    path('ConsultaVendasPorCliente/', ConsultaVendasPorCliente, name='ConsultaVendasPorCliente'),        
    path('ConsultaVendasPorPeriodo/', ConsultaVendasPorPeriodo, name='ConsultaVendasPorPeriodo'),        
    path('ConsultaItensVenda/<int:venda_id>/', ConsultaItensVenda, name='ConsultaItensVenda'),           
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
