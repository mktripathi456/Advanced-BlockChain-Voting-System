import custom_blockchain_local as custom_blockchain
import time
blockchain = custom_blockchain.Blockchain()

print('Current Blockchain Data')
blockchain.load_stored_blockchain()

print('\nAttacking...\n')
time.sleep(2)

blockchain.chain[1]['candidate']='Alien'

print('New Blockchain Data')
blockchain.update_stored_blockchain()
print('Attacking successful.')


