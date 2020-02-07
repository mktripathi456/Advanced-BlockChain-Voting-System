import datetime
import json
import hashlib
import pickle
from django.conf import settings
import os

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0',candidate="")
    
    def create_block(self, proof, previous_hash,candidate):           #candidate,unique_id should be args
        
        block = {'index':len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'candidate': candidate}                        #1st check if valid vote or not and then append
        self.chain.append(block)
        
        return block

    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof,candidate):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256((str(new_proof** 2 - previous_proof**2)+candidate).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self):
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256((str(proof** 2 - previous_proof**2)+block['candidate']).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_and_mine_block(self,candidate):
        previous_block = self.get_previous_block()
        previous_proof = previous_block['proof']
        proof = self.proof_of_work(previous_proof,candidate)
        previous_hash = self.hash(previous_block)
        block = self.create_block(proof, previous_hash,candidate) # new vote is casted
        
        print("a new block is mined")                      # new vote is casted
        

    def update_stored_blockchain(self):
        
        file_path = 'VotingUI/blockchain_DB_bin_candidate'
        filehandler = open(file_path, 'wb+') 
        pickle.dump(self.chain, filehandler)
        print(self.chain)
        print("blockchain data updated\n")                      
        
        
    def load_stored_blockchain(self):
        file_path = 'VotingUI/blockchain_DB_bin_candidate'
        file_path = open(file_path, 'rb')
        chain=pickle.load(file_path)
        print(chain)
        self.chain=chain
        print("blockchain data loaded\n")

