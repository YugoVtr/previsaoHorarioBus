# -*- coding: utf-8 -*-
BOT_NAME = 'bus'

SPIDER_MIDDLEWARES = {
    'bus.middlewares.BusSpiderMiddleware': 543,
}

SPIDER_MODULES = ['bus.spiders']
NEWSPIDER_MODULE = 'bus.spiders'

LOG_LEVEL = 'WARNING'
