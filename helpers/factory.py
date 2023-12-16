import sys
import traceback
from datetime import datetime

from termcolor import cprint

from config.settings import MIN_SLEEP, MAX_SLEEP, USE_SHUFFLE, CHAINS, STR_DONE, \
    SCHEDULE_TIME, CHECK_GWEI, MAX_RETRIES, UNUSED_REPEAT
from config.swap_routes import ROUTES
from helpers.cli import get_amount_in_range, get_int_in_range
from helpers.csv_helper import start_csv, write_csv_error, write_csv_success
from helpers.functions import sleeping, wait_schedule
from helpers.settings_helper import get_private_keys
from helpers.web3_helper import get_web3, check_status_tx, wait_gas
import time
from loguru import logger
import random

from modules.swaps.contract_map import ALL_FUNCTIONS

logger.remove()
logger.add(sys.stderr,
           format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level>| <level>{message}</level>")


def call_function(item, method, rpc_chain, _amount, params=[], csv='', retry=0):
    if CHECK_GWEI:
        wait_gas()

    web3 = get_web3(CHAINS[rpc_chain]['rpc'], item['proxy'])
    amount = get_amount_in_range(_amount)
    address = web3.eth.account.from_key(item['private_key']).address
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    csv_name = method.__name__

    if csv != '':
        csv_name = csv

    try:
        # tx_hash = method(web3, item['private_key'])

        logger.info(f'[{item["index"]}][{address}] | {method.__name__}')

        tx_hash = method(web3, item['private_key'], amount, *params)
        tx_link = f'{CHAINS[rpc_chain]["scan"]}/{tx_hash}'
        time.sleep(2)
        status = check_status_tx(web3, rpc_chain, tx_hash)
        if status == 1:
            logger.success(f'{STR_DONE} {rpc_chain} transaction: {tx_link}')

            write_csv_success(item['index'], {
                'status': 1,
                'csv_name': csv_name,
                'function': method.__name__,
                'date': formatted_datetime,
            })
            return True
        else:
            raise Exception(f'{rpc_chain} transaction failed: {tx_link}')
    except Exception as error:
        if retry < MAX_RETRIES:
            cprint(f'error retry...', 'red')
            call_function(item, method, rpc_chain, _amount, params, csv, retry + 1)
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            full_track_error = "".join(traceback_details)
            err_formated = traceback_details[2].strip()
            logger.error(full_track_error)

            write_csv_error(csv_name, [address, item['private_key'], method.__name__, params, full_track_error, formatted_datetime])


def run_script(method, rpc_chain, _amount, params=[], specific_prt={}):
    if SCHEDULE_TIME:
        wait_schedule(SCHEDULE_TIME)

    csv_name = method.__name__
    start_csv(csv_name)

    prt_keys = get_private_keys()
    # Filter by specific keys
    if specific_prt:
        prt_keys = [specific_prt]

    if USE_SHUFFLE:
        random.shuffle(prt_keys)

    for item in prt_keys:
        call_function(item, method, rpc_chain, _amount, params)
        sleeping(MIN_SLEEP, MAX_SLEEP)


def run_random_swap(routes, rpc_chain, _amount, specific_prt={}):
    if SCHEDULE_TIME:
        wait_schedule(SCHEDULE_TIME)

    csv_name_1 = 'random_zk_swap_1'
    csv_name_2 = 'random_zk_swap_2'
    start_csv(csv_name_1)
    start_csv(csv_name_2)

    prt_keys = get_private_keys()

    # Filter by specific keys
    if specific_prt:
        prt_keys = [specific_prt]

    if USE_SHUFFLE:
        random.shuffle(prt_keys)

    for item in prt_keys:
        random_dex = random.choice(list(routes.items()))
        random_dex = random_dex[1]
        random_token = random.choice(list(random_dex['tokens']))
        method = random_dex['function']

        additional_params = []
        if 'params' in random_dex:
            additional_params = random_dex['params']

        params = additional_params + ['', random_token]
        reverted_params = additional_params + [random_token, '']

        logger.info(f'Step 1 Sell ETH')
        step1_success = call_function(item, method, rpc_chain, _amount, params, csv_name_1)

        if step1_success:
            sleeping(MIN_SLEEP, MAX_SLEEP)
            logger.info(f'Step 2 Buy Back ETH')
            call_function(item, method, rpc_chain, '', reverted_params, csv_name_2)
            sleeping(MIN_SLEEP, MAX_SLEEP)


def run_multiple(functions: list, rpc_chain, prt_keys=[]):
    if len(prt_keys) == 0:
        prt_keys = get_private_keys()
    if USE_SHUFFLE:
        random.shuffle(prt_keys)
    wallets_paths = {}
    fn_len = len(sort_functions(functions))
    for fn_index in range(fn_len):
        for item in prt_keys:
            path = generate_path(item, wallets_paths, functions)
            function = path[fn_index]

            logger.info(f'Step {fn_index + 1}/{fn_len} - {function.__name__}')

            f_name = function.__name__

            if f_name == 'run_random_swap':
                run_random_swap(ROUTES, rpc_chain, '', item)


            elif f_name in ROUTES:
                extracted_route = {f_name: ROUTES[f_name]}
                run_random_swap(extracted_route, rpc_chain, '', item)
            else:
                run_script(function, rpc_chain, '', [], item)


def run_unused_fn(rpc_chain):
    prt_keys = get_private_keys()
    web3 = get_web3(CHAINS[rpc_chain]['rpc'])
    all_contracts = ALL_FUNCTIONS
    api_url = "https://block-explorer-api.mainnet.zksync.io/transactions"

    if USE_SHUFFLE:
        random.shuffle(prt_keys)

    for key in prt_keys:
        address = web3.eth.account.from_key(key['private_key']).address
        logger.info(f'Start on {address}')
        repeats = get_int_in_range(UNUSED_REPEAT)

        for step in range(repeats):
            logger.info(f'Step {step + 1}/{repeats}')
            tx_list = api_call(api_url, {
                'address': address,
                'limit': 100,
            })

            contract_addresses = set()

            for tx in tx_list['items']:
                to_address = tx['to']
                if to_address:
                    contract_addresses.add(web3.to_checksum_address(to_address))

            filtered_contracts = [value for key, value in all_contracts.items() if web3.to_checksum_address(key) not in contract_addresses]

            if len(filtered_contracts):
                random_fn = random.choice(filtered_contracts)

                if isinstance(random_fn, list):
                    # for Lending
                    logger.info(f'Random chosen  {random_fn[0].__name__} left {len(filtered_contracts)}')

                    run_script(random_fn[0], rpc_chain, '', [], key)
                    sleeping(30, 150)
                    run_script(random_fn[1], rpc_chain, '', [], key)


                elif random_fn.__name__ in ROUTES:
                    f_name = random_fn.__name__
                    logger.info(f'Random chosen  {f_name} left {len(filtered_contracts)}')
                    extracted_route = {f_name: ROUTES[f_name]}
                    run_random_swap(extracted_route, rpc_chain, '', key)
                else:
                    f_name = random_fn.__name__
                    logger.info(f'Random chosen  {f_name} left {len(filtered_contracts)}')

                    run_script(random_fn, rpc_chain, '', [], key)
            else:
                logger.info(f'No unused contracts found for   {address}')
                break


def generate_path(item, wallets_paths, functions):
    if not item['index'] in wallets_paths:
        random.shuffle(functions)
        sorted_functions = sort_functions(functions)
        wallets_paths[item['index']] = sorted_functions

    path = wallets_paths[item['index']]

    route_string = ", ".join(function.__name__ for function in path)
    cprint(f' Full Route: {route_string}', "yellow")

    return path


def sort_functions(functions):
    sorted_functions = []
    for function in functions:
        if isinstance(function, list):
            sorted_functions.extend(function)

        else:
            sorted_functions.append(function)
    return sorted_functions
