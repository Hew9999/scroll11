from termcolor import cprint

from modules.contracts.functions import *


def interface_contracts():
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'1. Swap tokens / mute.io', 'yellow')
            cprint(f'2. Swap tokens / zkswap.finance', 'yellow')



            cprint(f'0. Exit', 'yellow')
            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break

            elif option == '1':
                break


            elif option == '2':


                break

            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue
    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
