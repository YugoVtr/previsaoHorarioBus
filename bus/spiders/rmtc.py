# -*- coding: utf-8 -*-
import scrapy, re, logging, pprint, json
from datetime import datetime

class RmtcSpider(scrapy.Spider):
    name = 'rmtc'
    allowed_domains = ['m.rmtcgoiania.com.br']
    start_urls = ['http://m.rmtcgoiania.com.br']

    """
        inicia os parametros de execucao 
    """
    def __init__(self, termo_busca=None, numero_ponto=None, numero_linha=None, *args, **kwargs):
        super(RmtcSpider, self).__init__(*args, **kwargs)
        self.termo_busca = termo_busca
        self.numero_ponto = re.sub(r"[^0-9\.]+", "", numero_ponto)
        self.numero_linha = re.sub(r"[^0-9\.]+", "", numero_linha).lstrip("0")

    """
        Response: Pagina da home
        Comentario: E necessario passar por essa pagina para ir as demais 
            paginas do site 
    """
    def parse(self, response):
        return response.follow(url='/horariodeviagem', callback=self.horario_de_viagem)

    """
        Response: Pagina com os formularios para consulta
        Comentario: Nesta pagina e feita a consulta por numero do ponto 
            e atraves de pesquisa por termo (rua, bairro e/ou cidade).
    """
    def horario_de_viagem(self, response):
        assert self.termo_busca or self.numero_ponto or self.numero_linha, AssertionError("Missing parameters")
        callback = self.validar_horario_de_viagem
        
        if self.numero_ponto:
            formulario = {'txtNumeroPonto': self.numero_ponto, 'txtNumeroLinha': self.numero_linha}
        elif self.termo_busca:
            formulario = {'txtTermoBuscaPonto': self.termo_busca, 'txtPontoId':''}
        else:
            formulario = {"txtNumLinha": self.numero_linha}
            callback = self.validar_planeje_sua_viagem
                
        return scrapy.FormRequest.from_response(
            response,
            formdata=formulario,
            callback=callback
        )

    """
        Response: JSON que contem o resultado e a URL para proxima pagina
        Comentario: A url para a proxima pagina contem o(s) numero(s) do(s) 
            ponto(s) para serem consultados
    """
    def validar_horario_de_viagem(self, response):
        json_response = json.loads( response.body or '{"status":""}')
        if json_response['status'] == 'sucesso': 
            numeros_ponto = re.findall(r'[0-9]+', json_response['urldestino'])
            if 'linha' in json_response['urldestino']:
                numeros_ponto.pop()
            for numero_ponto in numeros_ponto:
                url = "/horariodeviagem/visualizar/ponto/{n_ponto}".format(n_ponto=numero_ponto)
                if self.numero_linha: 
                    url = "{url}/linha/{linha}".format(url=url, linha=self.numero_linha)
                yield response.follow(url=url, meta={"ponto":numero_ponto}, callback=self.resultado)
        elif json_response['status'] == 'erro':
            logging.error(json_response['mensagem'])
        else:
            logging.error("Erro desconhecido ao validar")

    """
        Response: JSON que contem o resultado e a URL para proxima pagina
        Comentario: A url para a proxima pagina contem o(s) numero(s) do(s) 
            ponto(s) para serem consultados
    """
    def validar_planeje_sua_viagem(self, response):
        return response.follow(
            url='/planejesuaviagem/kml/linha/{linha}'.format(linha=self.numero_linha),
            callback=self.planeje_sua_viagem
        )

    """
        Response: Pagina com os numeros dos pontos na linha (rota) indicada
        Comentario: Nesta pagina os numeros das rotas estao indicadas dentro de 
            tag JS
    """
    def planeje_sua_viagem(self, response):
        script = response.selector.css("script").get()
        pontos_json = re.findall(r'push\(\'(.*?)\'\);', script)
        for ponto_json in pontos_json:
            ponto_json = json.loads( ponto_json )
            url = "/horariodeviagem/visualizar/ponto/{n_ponto}".format(n_ponto=ponto_json['id'])
            yield response.follow(url=url, meta={"ponto":ponto_json['id']}, callback=self.resultado)

    """
        Response: Pagina com os previsoes de horarios
    """
    def resultado(self, response):
        linhas = response.selector.css('#sevico-horarioviagem .subtab-previsoes > tbody > tr')
        endereco = response.selector.xpath('//*[@id="sevico-horarioviagem"]/div/p[1]/text()[1]').get().strip()

        horarios = []
        for linha in linhas:
            numero_linha = linha.css('td::text')[0].get().lstrip("0")

            if (not self.termo_busca) and (self.numero_linha and self.numero_linha != numero_linha):
                continue
            
            horarios.append ( { 
                "numero_linha": numero_linha.zfill(3), 
                "horarios": {
                    'destino': linha.css('td::text')[1].get(), 
                    'proximo': re.sub(r"[^0-9\.]+", "", linha.css('td::text')[2].get()), 
                    'seguinte': re.sub(r"[^0-9\.]+", "", linha.css('td::text')[3].get())
                },
                "endereco": endereco
            })

        json = {
            "datahora_consulta": datetime.now(),  
            "numero_ponto": response.meta["ponto"], 
            "previsoes": horarios
        }
        yield json

        # scrapy.utils.response.open_in_browser(response)
        # import ipdb; ipdb.set_trace()
