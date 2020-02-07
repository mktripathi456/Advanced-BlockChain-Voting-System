import custom_blockchain_Voter_local as custom_blockchain_Voter
import sys

#Creating a Blockchain
if len(sys.argv)<3:
	print("Error in args. Should VoterID and Pointer")
	exit()

blockchain1 = custom_blockchain_Voter.Blockchain()
blockchain1.load_stored_blockchain()

blockchain1.add_and_mine_block(sys.argv[1],sys.argv[2])

#Saving Blockchain
blockchain1.update_stored_blockchain()
