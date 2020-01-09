.PHONY: run

BUSCA = 
PONTO = 
LINHA = 112

run: 
	scrapy crawl rmtc -o horario.json \
		-a termo_busca=$(BUSCA) \
		-a numero_ponto=$(PONTO) \
		-a numero_linha=$(LINHA)
