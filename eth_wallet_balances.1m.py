#!/usr/local/homebrew/bin/python3
"""Loads Ethereum wallet address (configured below) and all tokens associated with
   each address. Then displays current $USD value in the bitbar title, with a drop-down
   showing each total value for owned ETH and each token.
"""
import time
import operator
from collections import defaultdict

import requests

#
# Enter your wallets here:
#
WALLET_ADDRESSES = [
    '0x88752Bd600928b902EDAd9afFaaFCE1367Ae3461',
    '0x418091020F2A909479C4058E32BE08464A45DA8A',
]

# <bitbar.title>Etherum Wallet (and token) Balances</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Charlie Schluting</bitbar.author>
# <bitbar.author.github>manos</bitbar.author.github>
# <bitbar.desc>Displays a $USD total across all configured wallets, with drop-down showing the value of your ETH and all tokens held.</bitbar.desc>
# <bitbar.image>https://schluting.com/temp/bitbar-eth-bal.png</bitbar.image>
# <bitbar.dependencies>python3</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/manos/bitbar_ethereum_wallet_balances</bitbar.abouturl>

ETHEXPLORER_API_KEY = 'freekey'
EE_URL = 'http://api.ethplorer.io/'
EE_QS = '?apiKey=%s' % ETHEXPLORER_API_KEY

if __name__ == '__main__':
    eth_sum = 0
    my_tokens = defaultdict(lambda: 0)

    for addr in WALLET_ADDRESSES:
        res = requests.get(EE_URL + 'getAddressInfo/' + addr + EE_QS)
        res.raise_for_status()
        resp = res.json()

        eth_sum += resp.get('ETH', {}).get('balance', 0)

        if 'tokens' in resp and resp['tokens']:
            for token in resp['tokens']:
                if not token['balance']:
                    continue
                if int(token['tokenInfo']['decimals']):
                    # update the balance with proper decimal shift:
                    token['balance'] = token['balance'] * 10**-int(token['tokenInfo']['decimals'])
                # convert balance to USD now:
                if token['tokenInfo']['price']:
                    token_price = float(token['tokenInfo']['price']['rate'])
                else:
                    token_price = 0
                my_tokens[token['tokenInfo']['symbol']] += float(token['balance']) * token_price
        time.sleep(1)

    res = requests.get('https://api.coinmarketcap.com/v2/ticker/1027/')
    res.raise_for_status()
    resp = res.json()

    if resp['data']['symbol'] != 'ETH':
        raise "coinmarketcap.com API didn't return an ETH price!"

    eth_price = resp['data']['quotes']['USD']['price']
    my_eth_bal = float(eth_price) * float(eth_sum)

    # total $USD amount:
    total_bal = sum(my_tokens.values()) + my_eth_bal
    print("%.2f" % total_bal)
    print('---')
    print("ETH %.2f" % my_eth_bal)

    for token, bal in sorted(my_tokens.items(), key=operator.itemgetter(1), reverse=True):
        print(token, "%.2f" % bal)
    # links to wallet addresses on etherscan.io:
    for wallet in WALLET_ADDRESSES:
        print("Etherscan: %s" % wallet[:6] + "|href=https://etherscan.io/address/" + wallet)

    res = requests.get('https://api.coinmarketcap.com/v2/ticker/1/')
    res.raise_for_status()
    btc_price = res.json()['data']['quotes']['USD']['price']
    # print ETH and BTC prices:
    print("Prices:")
    print("BTC: %s" % str(btc_price))
    print("ETH: %s" % str(eth_price))

