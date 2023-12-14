import random
import traceback

from helpers.functions import get_min_balance
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import check_wait_web3_balance, get_token_balance
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.orbiter_bridge.functions import orbiter_eth_bridge
from modules.transfer.functions import map_recipients, transfer
from web3 import Web3
from scripts.functions import *
from scripts.orbiter.config import ETH_AMOUNT, NETWORKS


def script_orbiter():
    cprint("/-- Start Bridge process -->", "blue")

    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()

    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    okx_eth = get_okx_token_balance(0, 'ETH')
    if okx_eth < ETH_AMOUNT:
        cprint(f"Not enough ETH on OKX, need at least {ETH_AMOUNT} ETH", "red")

    recipient_map = map_recipients(recipients, private_keys)
    web3_linea = Web3(Web3.HTTPProvider(CHAINS['linea']['rpc']))
    try:
        wallet_num = 0
        for item in private_keys:
            wallet_num += 1
            private_key = item['private_key']

            run_orbiter_bridge(web3_linea, private_key, recipient_map[private_key], wallet_num)
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt as error:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit


def run_orbiter_bridge(web3_linea, private_key, recipient_wallet, wallet_num):
    wallet_address = web3_linea.eth.account.from_key(private_key).address
    pct = ETH_AMOUNT * 0.02
    amount = round(ETH_AMOUNT - random.uniform(0, pct), 4)

    # ------------------ Withdraw ------------------
    cprint(f"/-- Withdraw {amount} to wallet: [{wallet_num}]{wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.0002, 4), 'ETH', 'Linea', 'okx')
    sleeping(MIN_SLEEP, MAX_SLEEP)

    # ------------------ Start Bridge ------------------
    random.shuffle(NETWORKS)
    for bridge_network in NETWORKS:
        amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, '', amount * 0.98)
        #  balance left linea
        amount = amount - get_min_balance('linea')

        # BRIDGE FROM LINEA TO RANDOM NETWORK
        params = ['linea', bridge_network]
        run_script_one(orbiter_eth_bridge, private_key, 'linea', str(amount), params)

        # BRIDGE FROM RANDOM NETWORK TO LINEA
        web3_random = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))
        amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, '', amount * 0.98)
        params2 = [bridge_network, 'linea']
        #  balance left on random network
        amount = amount - get_min_balance(bridge_network)
        run_script_one(orbiter_eth_bridge, private_key, bridge_network, str(amount), params2)

    # ------------------ Withdraw to OKX ------------------
    amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, '', amount * 0.98)
    amount = amount - get_min_balance('linea')
    sleeping(MIN_SLEEP, MAX_SLEEP)
    cprint("/-- Withdraw to OKX", "blue")
    transfer(web3_linea, private_key, recipient_wallet, 'linea', '', amount)

    # ----------- Check OKX subAccount balances -------------
    while True:
        cprint("/-- Check OKX main account balance", "blue")
        main_acc_balance = get_okx_token_balance(0, 'ETH')
        if main_acc_balance >= amount:
            cprint(f"/-- {main_acc_balance} ETH found", "green")
            break
        else:
            for sub_account_num in range(1, 6):
                if len(config[f'OKX_SUB{sub_account_num}_API_KEY']) > 0:
                    cprint(f"/-- Check OKX subAccount {config[f'OKX_SUB{sub_account_num}_NAME']}", "blue")
                    acc_balance = get_okx_token_balance(sub_account_num, 'ETH')
                    if acc_balance >= amount * 0.99:
                        cprint(f"{acc_balance} ETH found, transfer to OKX main account", "green")
                        account = get_okx_account()
                        account.transfer("ETH", acc_balance, config[f'OKX_SUB{sub_account_num}_NAME'], 'master')
                        time.sleep(2)
                        break
        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue
