from config.multiple_routes import USE_FUNCTIONS
from config.swap_routes import ROUTES
from helpers.cli import *
from helpers.factory import run_random_swap, run_multiple, run_unused_fn
from modules.balance.module import interface_check_balance
from modules.contracts.module import interface_contracts
from modules.exchange_withdraw.module import interface_exchange_withdraw
from modules.orbiter_bridge.module import interface_orbiter_bridge
from modules.swaps.module import interface_swaps
from modules.transfer.module import interface_transfer
from config.settings import  ZKSYNC_ETH_AMOUNT_PER_ACC
from modules.withdraw_block.module import interface_withdraw

if __name__ == '__main__':
    try:
        while True:
            cprint(f'Select an action:', 'yellow')
            cprint(f'0. Exit', 'yellow')
            cprint(f'1. Check Balances', 'yellow')
            cprint(f'2. Transfer Tokens', 'yellow')
            cprint(f'3. Exchange Withdraw', 'yellow')

            cprint(f'-------- BRIDGE/SWAP --------', 'blue')
            cprint(f'4. Orbiter Bridge', 'yellow')
            cprint(f'5. Swaps JediSwap/MySwap/10kSwap...', 'yellow')

            cprint(f'-------- Own Contracts --------', 'blue')
            cprint(f'6. Interact  with contracts', 'yellow')

            cprint(f'7. Withdraw at block', 'yellow')



            # cprint(f'---------- VOLUME wallet by wallet ----------', 'blue')
            # cprint(f'11. View volume options',
            #        'yellow')
            #
            # cprint(f'---------- Random Swaps ----------', 'blue')
            # cprint(f'12. Swap ETH <=> Random Token / Random Dex',
            #        'yellow')
            #
            # cprint(f'---------- Multiple Functions ----------', 'blue')
            # cprint(f'13. Run multiple functions configured in config/multiple_routes.py',
            #        'yellow')
            #
            # cprint(f'---------- Unused Functions ----------', 'blue')
            # cprint(f'14. Find and run unused contract for wallet ',
            #        'yellow')

            # cprint(f'24. Starknet ETH: OKX > Starknet > {STARKNET_TX_REPEATS} Swaps > OKX', 'yellow')

            option = input("> ")

            if option == '0':
                cprint(f'Exit, bye bye.', 'green')
                break
            elif option == '1':
                interface_check_balance()
                break
            elif option == '2':
                interface_transfer()
                break
            elif option == '3':
                interface_exchange_withdraw()
                break



            elif option == '4':
                interface_orbiter_bridge()
                break


            elif option == '5':
                interface_swaps()
                break

            elif option == '6':
                interface_contracts()
                break


            elif option == '7':
                interface_withdraw()
                break


            # elif option == '11':
            #     interface_zksync_volume()
            #     break
            # elif option == '12':
            #     amount_str = print_input_amounts_range('Swap amount')
            #     run_random_swap(ROUTES, 'zksync', amount_str)
            # elif option == '13':
            #     run_multiple(USE_FUNCTIONS, 'zksync')
            #     break
            #
            #
            # elif option == '14':
            #     run_unused_fn('zksync')
            #     break


            else:
                cprint(f'Wrong action. Please try again.\n', 'red')
                continue


    except KeyboardInterrupt:
        cprint(f' Exit, bye bye\n', 'red')
        raise SystemExit
