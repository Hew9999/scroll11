import asyncio

from loguru import logger
import time

from config.settings import CHAINS, TOKEN_ADDRESSES, TRANSFER_TO
from helpers.settings_helper import  get_private_keys_txt
from helpers.web3_helper_async import get_web3
from modules.transfer.functions_async import transfer


def interface_withdraw():

    private_keys = get_private_keys_txt()
    web3 = get_web3(CHAINS['ethereum']['rpc'])



    try:

        block=web3.eth.block_number


        while True:
            check_block=web3.eth.block_number


            if check_block!=block:
                logger.info(f'New block found: {check_block}' )
                block=check_block

                tasks=send_tokens(web3,private_keys)
                if tasks:
                    await asyncio.gather(*tasks)



            time.sleep(2)
    except KeyboardInterrupt:
        print("Polling stopped due to user interruption")




def send_tokens(web3,private_keys):
    tasks=[]
    for item in private_keys:
        private_key = item['private_key']
        address = TRANSFER_TO
        for token_address in TOKEN_ADDRESSES:
            tasks.append(asyncio.create_task(transfer(web3, private_key, address, 'ethereum', token_address,0)))
    return tasks


