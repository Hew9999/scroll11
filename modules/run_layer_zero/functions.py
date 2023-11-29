
from helpers.web3_helper import *
from helpers.functions import *
from modules.run_layer_zero.config import *





def stargate_bridge_usdv(web3, private_key, amount,from_chain, to_chain,from_token, retry=0):
        account = web3.eth.account.from_key(private_key)
        wallet = account.address
        router_address= web3.to_checksum_address(ARBITRUM_STARGATE_BRIDGE_CONTRACT)
        router_contract = web3.eth.contract(address=router_address, abi=ABI_STARGATE_BRIDGE_V1)

        address_contract = web3.to_checksum_address(SWAP_RECOLOR_CONTRACTS[from_chain])


        bridge_contract = web3.eth.contract(address=address_contract, abi=SWAP_RECOLOR_ABI)


        token_contract, token_decimal, symbol = check_data_token(web3, from_token)


        if not  amount:
            amount = get_token_balance(web3, wallet, from_token)
        else:
            amount = int_to_wei(amount,6)

        cprint(f'/-- {symbol} {wei_to_int(amount, token_decimal)} {from_chain} => {to_chain} for USDV {wallet} -->', 'green')


        allowance_amount = check_allowance(web3, from_token, wallet, address_contract)
        if amount > allowance_amount:
            cprint(f'/-- Approve token: USDT', 'green')
            approve_token(web3, private_key, from_chain, from_token, address_contract)
            sleeping(5, 10)



        lz_fee = stargate_lz_fee(wallet, from_chain, to_chain, router_contract)
        print('LZ Fees:', wei_to_int(lz_fee, 18))
        min_amount=amount-50
        swap_params = [from_token, amount, min_amount]
        wallet_bytes = wallet.replace('0x', '0x000000000000000000000000')

        param = [wallet_bytes, amount, min_amount, LZ_CHAIN_IDS[to_chain]]
        extra_options='0x00010000000000000000000000000000000000000000000000000000000000029810'
        msg_fee=[lz_fee, 0]
        compose_msg=b''



        chain_id = web3.eth.chain_id

        contract_txn = bridge_contract.functions.swapRecolorSend(
            swap_params,
            3,
            param,
            extra_options,
            msg_fee,
            wallet,
            compose_msg
        ).build_transaction(
            {
                'from': wallet,
                'nonce': web3.eth.get_transaction_count(wallet),
                'value': int(lz_fee),
                'gasPrice': 0,
                'gas': 0,
            }
        )
        contract_txn = add_gas_price(web3, contract_txn, chain_id)
        contract_txn = add_gas_limit(web3, contract_txn, chain_id)
        tx_hash = sign_tx(web3, contract_txn, private_key)
        return tx_hash




































