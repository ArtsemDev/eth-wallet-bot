from web3 import Web3


web3 = Web3(Web3.HTTPProvider("https://eth.drpc.org"))
web3.eth.account.enable_unaudited_hdwallet_features()
account, mnemonic = web3.eth.account.create_with_mnemonic()
hash = web3.eth.send_transaction(transaction={
    "from": account.address,
    "to": account.address,
    "value": 1000000
})
print(hash)