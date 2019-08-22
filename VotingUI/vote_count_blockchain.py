import custom_blockchain
blockchain = custom_blockchain.Blockchain()

blockchain.load_stored_blockchain()

candidates={}
for block in blockchain.chain:
    voted_candidate=block['candidate']
    if voted_candidate in candidates.keys():
        candidates[voted_candidate]+=1
    else:
        candidates[voted_candidate]=1

for candidate in candidates.keys():
    print(candidate,candidates[candidate])