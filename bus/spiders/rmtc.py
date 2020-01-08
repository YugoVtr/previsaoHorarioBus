# -*- coding: utf-8 -*-
import scrapy, re, logging
from datetime import datetime

class RmtcSpider(scrapy.Spider):
    name = 'rmtc'
    allowed_domains = ['m.rmtcgoiania.com.br']
    start_urls = ['http://m.rmtcgoiania.com.br']

    def __init__(self, numero_ponto=None, numero_linha=None, *args, **kwargs):
        super(RmtcSpider, self).__init__(*args, **kwargs)
        self.numero_ponto = numero_ponto
        self.numero_linha = numero_linha
        # Configuracao de log
        scrapy.utils.log.configure_logging(install_root_handler=False)
        logging.basicConfig(
            filename="logs/{0}.log".format( self.name ),
            level=logging.DEBUG
        )

    def parse(self, response):
        return response.follow(url='/horariodeviagem', callback=self.horario)

    def horario(self, response):
        url = "/horariodeviagem/visualizar/ponto/{n_ponto}".format(n_ponto=self.numero_ponto)
        if self.numero_linha: 
            url = "{url}/linha/{linha}".format(url=url, linha=self.numero_linha)
        return response.follow(url=url, callback=self.resultado)

    def resultado(self, response):
        linhas = response.selector.css('#sevico-horarioviagem .subtab-previsoes > tbody > tr')
        horarios = []
        for linha in linhas:
            horarios.append ( { 
                linha.css('td::text')[0].get(): {
                    'destino': linha.css('td::text')[1].get(), 
                    'proximo': re.sub(r"[^0-9\.]+", "", linha.css('td::text')[2].get()), 
                    'seguinte': re.sub(r"[^0-9\.]+", "", linha.css('td::text')[3].get())
                }
            })

        json = {
            "datahora_consulta": datetime.now(),  
            self.numero_ponto: horarios
        }
        logging.warning(json)
        yield json

        # import ipdb; ipdb.set_trace()
