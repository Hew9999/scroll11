import random
import traceback

from helpers.functions import get_min_balance
from helpers.settings_helper import get_recipients, get_private_keys
from helpers.web3_helper import check_wait_web3_balance, get_token_balance
from modules.exchange_withdraw.cli import *
from modules.exchange_withdraw.functions import call_exchange_withdraw
from modules.orbiter_bridge.functions import orbiter_eth_bridge, orbiter_token_bridge
from modules.transfer.functions import map_recipients, transfer
from web3 import Web3
from scripts.functions import *
from scripts.orbiter.config import ETH_AMOUNT, NETWORKS, USDT_AMOUNT, USDT_ADDRESES


def script_orbiter_eth():
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

            run_orbiter_bridge_eth(web3_linea, private_key, recipient_map[private_key], wallet_num)
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt as error:
        cprint(f' Exit, bye bye\n', 'red')
        # raise SystemExit


def run_orbiter_bridge_eth(web3_linea, private_key, recipient_wallet, wallet_num):
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


def script_orbiter_usdt():
    cprint("/-- Start Bridge process -->", "blue")

    recipients = get_recipients('okx_address')
    private_keys = get_private_keys()

    if len(recipients) != len(private_keys):
        cprint("Wrong recipients count in recipients.txt, should be 1 sender = 1 recipient", "red")
        return

    okx_eth = get_okx_token_balance(0, 'USDT')
    if okx_eth < USDT_AMOUNT:
        cprint(f"Not enough USDT on OKX, need at least {USDT_AMOUNT} USDT", "red")

    recipient_map = map_recipients(recipients, private_keys)
    try:
        wallet_num = 0
        for item in private_keys:
            wallet_num += 1
            private_key = item['private_key']

            run_orbiter_bridge_usdt(private_key, recipient_map[private_key], wallet_num)
            sleeping(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt as error:
        cprint(f' Exit, bye bye\n', 'red')
        # raise SystemExit


def run_orbiter_bridge_usdt(private_key, recipient_wallet, wallet_num):
    web3_op = Web3(Web3.HTTPProvider(CHAINS['optimism']['rpc']))
    web3_linea = Web3(Web3.HTTPProvider(CHAINS['linea']['rpc']))

    wallet_address = web3_linea.eth.account.from_key(private_key).address
    pct = USDT_AMOUNT * 0.01
    amount = round(USDT_AMOUNT - random.uniform(0, pct), 4)

    # ------------------ Withdraw ------------------
    cprint(f"/-- Withdraw {amount} to wallet: [{wallet_num}]{wallet_address}", "blue")
    call_exchange_withdraw(wallet_address, round(amount + 0.2, 2), 'USDT', 'Optimism', 'okx')

    sleeping(MIN_SLEEP, MAX_SLEEP)

    amount = check_wait_web3_balance(web3_op, 'optimism', wallet_address, USDT_ADDRESES['optimism'], amount * 0.98)

    # ------------------ #BRIDGE FROM OP ------------------
    params = ['optimism', 'linea', USDT_ADDRESES['optimism']]
    run_script_one(orbiter_token_bridge, private_key, 'optimism', '', params)

    # ------------------ Start Bridge ------------------
    random.shuffle(NETWORKS)
    for bridge_network in NETWORKS:
        amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, USDT_ADDRESES['linea'], amount * 0.98)

        # BRIDGE FROM LINEA TO RANDOM NETWORK
        params = ['linea', bridge_network, USDT_ADDRESES['linea']]
        run_script_one(orbiter_token_bridge, private_key, 'linea', '', params)

        # BRIDGE FROM RANDOM NETWORK TO LINEA
        web3_random = Web3(Web3.HTTPProvider(CHAINS[bridge_network]['rpc']))
        amount = check_wait_web3_balance(web3_random, bridge_network, wallet_address, USDT_ADDRESES[bridge_network], amount * 0.98)
        params2 = [bridge_network, 'linea', USDT_ADDRESES[bridge_network]]
        run_script_one(orbiter_eth_bridge, private_key, bridge_network, '', params2)

    # ------------------ #BRIDGE TO OP ------------------
    amount = check_wait_web3_balance(web3_linea, 'linea', wallet_address, USDT_ADDRESES['linea'], amount * 0.98)
    params = ['linea', 'optimism', USDT_ADDRESES['linea']]
    run_script_one(orbiter_token_bridge, private_key, 'linea', '', params)

    # ------------------ Withdraw to OKX ------------------
    amount = check_wait_web3_balance(web3_op, 'optimism', wallet_address, USDT_ADDRESES['optimism'], amount * 0.98)
    sleeping(MIN_SLEEP, MAX_SLEEP)
    cprint("/-- Withdraw to OKX", "blue")
    transfer(web3_op, private_key, recipient_wallet, 'optimism', USDT_ADDRESES['optimism'], amount)

    # ----------- Check OKX subAccount balances -------------
    while True:
        cprint("/-- Check OKX main account balance", "blue")
        main_acc_balance = get_okx_token_balance(0, 'USDT')
        if main_acc_balance >= amount:
            cprint(f"/-- {main_acc_balance} USDT found", "green")
            break
        else:
            for sub_account_num in range(1, 6):
                if len(config[f'OKX_SUB{sub_account_num}_API_KEY']) > 0:
                    cprint(f"/-- Check OKX subAccount {config[f'OKX_SUB{sub_account_num}_NAME']}", "blue")
                    acc_balance = get_okx_token_balance(sub_account_num, 'USDT')
                    if acc_balance >= amount * 0.99:
                        cprint(f"{acc_balance} ETH found, transfer to OKX main account", "green")
                        account = get_okx_account()
                        account.transfer("USDT", acc_balance, config[f'OKX_SUB{sub_account_num}_NAME'], 'master')
                        time.sleep(2)
                        break
        sleeping(MIN_SLEEP, MAX_SLEEP)
        continue
