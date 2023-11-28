from termcolor import cprint

from helpers.cli import print_input_amounts_range
from helpers.factory import run_script
from modules.contracts.functions import *


def interface_contracts():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Deposit to contract', 'yellow')
            cprint(f'2. Withdraw from contract', 'yellow')
            cprint(f'3. Claim rewards', 'yellow')



            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                amount_str = print_input_amounts_range('Deposit amount')
                run_script(stake, 'scroll', amount_str, [])
                break


            elif option == '2':
                run_script(withdraw, 'scroll',0, [])

                break

            elif option == '3':
                run_script(claim, 'scroll', 0, [])

                break

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
