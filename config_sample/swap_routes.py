from modules.swaps.functions import *
from modules.swaps.config import TOKENS

ROUTES={
    'swap_token_spacefi':{
        'tokens':{TOKENS['USDC'], TOKENS['USDT']},
        'function': swap_token_spacefi

    },


    'open_ocean':{
        'tokens':{
            TOKENS['USDC'],
            TOKENS['USDT'],
            # ZKSYNC_TOKENS['BUSD'],
        },
        'function': open_ocean

    },


}