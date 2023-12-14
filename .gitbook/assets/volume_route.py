from modules.inch_swap.functions import inch_swap
from modules.run_zksync.functions import *
from modules.run_zksync.config import ZKSYNC_TOKENS
from modules.woofi_swap.functions import woofi_swap

VOLUME_ROUTES={

    'odos_swap':{
        'tokens':[
            ZKSYNC_TOKENS['USDC'],
            ZKSYNC_TOKENS['BUSD'],
            ZKSYNC_TOKENS['USDT'],
            ZKSYNC_TOKENS['USD+'],
        ],
        'function': odos_swap

    },

    'inch_swap': {
        'tokens': [
            ZKSYNC_TOKENS['USDC'],
            ZKSYNC_TOKENS['USD+'],

        ],
        'function': inch_swap,
        'params': ['zksync']

    },
    # 'swap_pancake': {
    #     'tokens': {
    #         ZKSYNC_TOKENS['USDT'],
    #         ZKSYNC_TOKENS['USDC'],
    #     },
    #     'function': swap_pancake,
    #
    # },

    'open_ocean': {
        'tokens': [
            ZKSYNC_TOKENS['USD+'],
            ZKSYNC_TOKENS['USDC'],
            ZKSYNC_TOKENS['BUSD'],
            ZKSYNC_TOKENS['USDT'],
        ],
        'function': open_ocean

    },



}