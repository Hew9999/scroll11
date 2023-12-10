import random
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import  check_wait_web3_balance
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.run_layer_zero.config import *
from modules.run_layer_zero.functions import  stargate_bridge_usdv
from modules.transfer.functions import map_recipients, transfer
from web3 import Web3
from scripts.functions import *
from scripts.layer_zero.config import *


def script_usdv_layer_zero():
    cprint("/-- Start USDV process -->", "blue")

    recipients = get_recipients('bitget_address')
    private_keys = get_private_keys()
    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    bitget_usdt = get_bitget_token_balance('USDT')
    if bitget_usdt < LZ_SCRIPT_USDT_AMOUNT:
        cprint(f"Not enough USDT on Bitget, need at least {LZ_SCRIPT_USDT_AMOUNT} USDT", "red")

    recipient_map = map_recipients(recipients, private_keys)
    web3_bsc = Web3(Web3.HTTPProvider(CHAINS['bsc']['rpc']))
    web3_arbitrum = Web3(Web3.HTTPProvider(CHAINS['arbitrum']['rpc']))

    try:
        wallet_num = 0
        for private_key in get_private_keys():
            wallet_num += 1
            run_usdv_one_wallet(web3_bsc, web3_arbitrum, private_key, recipient_map[private_key], wallet_num)
            sleeping(SCRIPT_MIN_SLEEP, SCRIPT_MAX_SLEEP)
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def run_usdv_one_wallet(web3_bsc, web3_arbitrum, private_key, recipient_wallet, wallet_num):
    amount = round(LZ_SCRIPT_USDT_AMOUNT - random.uniform(0, 2), 2)

    # ------------------ Withdraw ------------------
    wallet_address = web3_bsc.eth.account.from_key(private_key).address
    cprint(f"/-- Withdraw {amount} USDT from bitget to wallet: {wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.2, 2), 'USDT', 'ArbitrumOne', 'bitget')

    sleeping(SCRIPT_MIN_SLEEP, SCRIPT_MAX_SLEEP)

    # ------------------ Check Arbitrum balance ------------------
    check_wait_web3_balance(web3_arbitrum, 'arbitrum', wallet_address, ARB_USDT_ADDRESS, amount)


    sleeping(2, 3)

    stargate_bridge_usdv(web3_arbitrum, private_key, 'arbitrum', 'bsc', ARB_USDT_ADDRESS)

    sleeping(SCRIPT_MIN_SLEEP, SCRIPT_MAX_SLEEP)

    # ------------------ Check BSC balance ------------------
    amount=check_wait_web3_balance(web3_bsc, 'BSC', wallet_address, USDV_TOKEN_ADDRESS['bsc'], amount)
    sleeping(2, 3)


    # ------------------ Withdraw to Bitget ------------------
    cprint("/-- Withdraw to Bitget", "blue")

    transfer(web3_bsc, private_key, recipient_wallet, 'bsc', USDV_TOKEN_ADDRESS['bsc'], 0)

    sleeping(SCRIPT_MIN_SLEEP, SCRIPT_MAX_SLEEP)

    while True:
        sleeping(SCRIPT_MIN_SLEEP*2, SCRIPT_MAX_SLEEP*2)
        cprint("/-- Check Bitget USDV balance", "blue")
        bitget_usdv = get_bitget_token_balance('USDV')
        if bitget_usdv >= amount:
            cprint(f"/-- {bitget_usdv} USDV found, continue...", "green")
            break

    cprint(f"/-- {bitget_usdv} Create sell order USDV/USDT amount:{bitget_usdv} price:{USDV_LIMI_PRICE}", "blue")

    symbol = 'USDVUSDT_SPBL'
    order_info = sell_token(symbol, USDV_LIMI_PRICE, bitget_usdv)

    while True:
        cprint(f"/-- {bitget_usdv} Check order status ", "blue")
        order_info = get_order_info(order_info['id'], order_info['symbol'])
        if order_info['status'] == 'closed':
            cprint(f"/-- {bitget_usdv} Order closed", "green")
            break
        else:
            sleeping(SCRIPT_MIN_SLEEP*2, SCRIPT_MAX_SLEEP*2)
            continue
