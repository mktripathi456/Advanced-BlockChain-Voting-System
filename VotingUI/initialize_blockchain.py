import VotingUI.custom_blockchain as custom_blockchain
import VotingUI.custom_blockchain_VotingStatus as custom_blockchain_VotingStatus


#Creating a Blockchain
blockchain1 = custom_blockchain.Blockchain()
blockchain2 = custom_blockchain_VotingStatus.Blockchain()

#Saving Blockchain
blockchain1.update_stored_blockchain()

#Saving Blockchain
blockchain2.update_stored_blockchain()
