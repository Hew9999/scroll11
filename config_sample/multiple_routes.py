from helpers.factory import run_random_swap
from modules.swaps.functions import *

"""
You can use:
swap_token_spacefi
open_ocean

______________________________________________________
You can add functions to [] ,
example [module_1, module_2, [module_3, module_4], module 5]
The script will start module 3 and 4 sequentially, others modules 
module_1,module_2,module_5 will start randomly

You can duplicate function for example: [run_random_swap,run_random_swap,run_random_swap]
for swaps in different protocols

"""

USE_FUNCTIONS=[

    run_random_swap,

]







