from django.shortcuts import render,redirect
import sqlite3
import sys,os,time
import hashlib
from collections import defaultdict
import VotingUI.custom_blockchain as custom_blockchain
import VotingUI.custom_blockchain_Voter as custom_blockchain_Voter
import VotingUI.custom_blockchain_VotingStatus as custom_blockchain_VotingStatus


voter_id=''
logged_in=False
constituency=''
constituency_id=''
pointer=''
adminlogged=False
electionstatus=True

voterBlockchain = custom_blockchain_Voter.Blockchain()
voterBlockchain.load_stored_blockchain()


def main_page(request):
    global voter_id
    global logged_in
    constituency=''
    voterid=''
    req=request.GET
    print('main ',req)
    return render(request, 'Demo.html')


def main_page2(request):
    global voter_id
    global logged_in
    req=request.GET
    print(req['state'])
    print('\n\n main2 ',req,'\n\n')
    db = sqlite3.connect('voter1.db')
    cursor = db.cursor()
    print('\n\n',req,'\n\n')
    stmt=f"SELECT name,constituencyid from constituency where state='{req['state'][1:]}'"
    print(stmt)
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print('\n constituencies:- ',all_rows)
    state=req['state']
    return render(request, 'Demo2.html',{'dict1':all_rows})

def otp_open(request):
    global voter_id
    global constituency
    global constituency_id
    global logged_in
    global pointer
    global electionstatus
    req=request.GET
    print('\n\n',req,'\n\n')
    
    if electionstatus==False:
        return render(request,'Demo3.html',{'dict1':[req['constituency']]})
    
    pointerGot=voterBlockchain.search_voterID_and_return_pointer(req['voter'])
    if pointerGot=='Not Found':
        return render(request,'Demo3.html',{'dict1':[req['constituency']]})
    pointer=pointerGot
    print(f"pointer={pointer}")

    db = sqlite3.connect('voter1.db')
    cursor = db.cursor()
    stmt=f"SELECT count(*) from user where pointer='{pointer}' and phonenumber='{req['phone']}'"
    
    print(stmt)
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    if all_rows[0][0]==0:
        return render(request,'Demo3.html',{'dict1':[req['constituency'],]})

    stmt=f"SELECT count(*) from searchOptimization where voterid='{req['voter']}'"
    print(stmt)
    
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    

    votingStatusBC=custom_blockchain_VotingStatus.Blockchain()
    votingStatusBC.load_stored_blockchain()
    
    if all_rows[0][0]==0:

        found=votingStatusBC.search_voterID(req['voter'])
        if found==0:
        
            stmt=f"SELECT constituencyid from constituency where name='{req['constituency']}'"
            print(stmt)
            cursor.execute(stmt)
            all_rows = cursor.fetchall()
            print(all_rows)
            constituency_id=all_rows[0][0]
            
            voter_id=req['voter']
            print(constituency_id)
            token=hashlib.sha1((voter_id+str(time.time())).encode()).hexdigest()
            token=token[:8].upper()
            print(token)

            stmt=f"Update user set otp='{token}' where pointer='{pointer}'"
            print(stmt)
            cursor.execute(stmt)
            db.commit()

            db.close()
            logged_in=True
            return render(request, 'otp.html',{'dict1':[token]})
        else:
            pointer=''
            voter_id=''
            return render(request, 'Alert.html')

    stmt=f"SELECT BlockID from searchOptimization where voterid='{req['voter']}'"
    print(stmt)
    
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    blockID=int(all_rows[0][0])

    print(f"blockID={blockID}")
    print(f"len={len(votingStatusBC.chain)})")
    if blockID>=len(votingStatusBC.chain):
        pointer=''
        voter_id=''
        logged_in=False
        return render(request, 'Alert.html')
    
    found_voterID=votingStatusBC.chain[blockID]['voter']
    if found_voterID==req['voter']:
        return render(request,'Demo3.html',{'dict1':[req['constituency']]})
    else:
        pointer=''
        voter_id=''
        logged_in=False
        return render(request, 'Alert.html')

def otp_verify(request):
    global voter_id
    global logged_in
    global constituencyid
    global pointer
    print(logged_in)
    if(logged_in is False):
        return render(request,'Demo.html')
    req=request.GET

    db = sqlite3.connect('voter1.db')
    cursor = db.cursor()
    print('\n\n',req,'\n\n')
    
    cursor.execute(f"SELECT count(*) from user where pointer='{pointer}' and otp='{req['otp']}'")
    all_rows = cursor.fetchall()
    print(all_rows)

    if all_rows[0][0]==0:
        return render(request, 'otp2.html')
    else:
        stmt=f"select name, party,candidateid from candidate where constituencyid={constituency_id}"
        print(stmt)
        cursor.execute(stmt)
        all_rows = cursor.fetchall()
        print(all_rows)
        return render(request, 'voting.html',{'dict1':all_rows})

def candidate_vote(request):
    global logged_in
    global voter_id
    if(logged_in is False):
        return render(request,'Demo.html')
    req=request.GET
    print(req)
    
    candidate=list(req.keys())[0]
    
    candidate_blockchain = custom_blockchain.Blockchain()
    candidate_blockchain.load_stored_blockchain()

    verify_data=candidate_blockchain.is_chain_valid()
    votingStatusBC=custom_blockchain_VotingStatus.Blockchain()
    votingStatusBC.load_stored_blockchain()
    
    if verify_data:
        candidate_blockchain.add_and_mine_block(candidate)
        candidate_blockchain.update_stored_blockchain()

        votingStatusBC.add_and_mine_block(voter_id)
        votingStatusBC.update_stored_blockchain()
        
        blockID=len(votingStatusBC.chain)-1

        db = sqlite3.connect('voter1.db')
        cursor = db.cursor()
        
        stmt=f"insert into searchOptimization values('{voter_id}','{blockID}')"
        
        print(stmt)
        cursor.execute(stmt)
        
        db.commit()
    else:
        return render(request, 'Alert.html')


    logged_in=False
    voter_id=''
    pointer=''
    candidates=[i['candidate'] for i in candidate_blockchain.chain]
    party=defaultdict(int)
    print(candidates)
    
    for i in candidates[1:]:
        stmt=f"select party from candidate where candidateid='{i}'"
        print(stmt)
        cursor.execute(stmt)
        all_rows = cursor.fetchall()
        party[all_rows[0][0]]+=1
    party_list=[i for i in party.items()]
    print(party_list)
    return render(request, 'thanks.html',{'dict1':voterBlockchain.chain,'dict2':candidate_blockchain.chain,'dict3':votingStatusBC.chain,'dict4':party_list})


def admin_login(request):
    global voter_id
    global logged_in
    global electionstatus
    global adminlogged
    constituency=''
    voterid=''
    req=request.GET
    print('main ',req)

    if req=={}:
    	return render(request, 'Admin_login.html')
    else:
    	if req['uname']=='admin' and req['password']=='admin':
	    	adminlogged=True
	    	if electionstatus==True:
	    		return render(request, 'Admin_finish.html')
	    	else:
	    		return render(request, 'Admin_start.html')
    return render(request, 'Admin_login.html')


def admin_start(request):
    global voter_id
    global logged_in
    global electionstatus
    global adminlogged
    logged_in=False
    constituency=''
    voterid=''

    if adminlogged==False:
    	return render(request, 'Admin_login.html')
    req=request.GET
    print('main ',req)
    if electionstatus==False:
	    electionstatus=True
	    exec(open("VotingUI/initialize_blockchain.py").read())
	    db = sqlite3.connect('voter1.db')
	    cursor = db.cursor()
	    
	    stmt=f"Delete from searchOptimization"
	    print(stmt)
	    cursor.execute(stmt)
	    db.commit()


    return render(request, 'Admin_finish.html')

def admin_end(request):
    global voter_id
    global logged_in
    global electionstatus
    logged_in=False
    electionstatus=False
    constituency=''
    voterid=''
    req=request.GET
    print('main ',req)
    
    if adminlogged==False:
    	return render(request, 'Admin_login.html')
    
    return render(request, 'Admin_start.html')


def admin_logout(request):
    global voter_id
    global logged_in
    global adminlogged
    logged_in=False
    adminlogged=False
    constituency=''
    voterid=''
    req=request.GET
    print('main ',req)
    return render(request, 'Demo.html')


def results(request):
    global electionstatus
    constituency=''
    voterid=''
    
    req=request.GET
    
    if electionstatus==True:
    	return render(request, 'Demo.html')

    candidate_blockchain = custom_blockchain.Blockchain()
    candidate_blockchain.load_stored_blockchain()

    candidates=[i['candidate'] for i in candidate_blockchain.chain]
    party=defaultdict(int)
    print(candidates)
    db = sqlite3.connect('voter1.db')
    cursor=db.cursor()
    for i in candidates[1:]:
        stmt=f"select party from candidate where candidateid='{i}'"
        print(stmt)
        cursor.execute(stmt)
        all_rows = cursor.fetchall()
        party[all_rows[0][0]]+=1
    party_list=[i for i in party.items()]
    print(party_list)

    total_votes=0
    for i in party_list:
    	total_votes+=i[1]
    print(total_votes)
    if total_votes==0:
    	return render(request, 'Demo.html')
    percentage=[]
    for i in party_list:
    	percentage.append((i[0],i[1]*100/total_votes))
    print(percentage)
    return render(request, 'result.html',{'dict4':party_list,'dict2':percentage})
