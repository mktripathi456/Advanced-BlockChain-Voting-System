from django.shortcuts import render,redirect
import sqlite3
import sys,os,time
import hashlib
from collections import defaultdict
import VotingUI.custom_blockchain as custom_blockchain

voter_id=''
logged_in=''
constituency=''
constituency_id=''

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
    stmt=f"SELECT name,constituencyid from constituency where state='{req['state']}'"
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
    req=request.GET
    db = sqlite3.connect('voter1.db')
    cursor = db.cursor()
    print('\n\n',req,'\n\n')
    stmt=f"SELECT count(*) from user where voterid='{req['voter']}' and phonenumber='{req['phone']}'"
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    if all_rows[0][0]==0:
        return render(request,'Demo3.html',{'dict1':[req['constituency'],]})
    
    stmt=f"SELECT voted from election where voterid='{req['voter']}'"
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    if all_rows[0][0]=='1':
        return render(request,'Demo3.html',{'dict1':[req['constituency']]})

    stmt=f"SELECT constituencyid from constituency where name='{req['constituency']}'"
    print(stmt)
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    constituency_id=all_rows[0][0]
    
    stmt=f"SELECT count(*) from election where voterid='{req['voter']}' and constituencyid='{constituency_id}'"
    print(stmt)
    cursor.execute(stmt)
    all_rows = cursor.fetchall()
    print(all_rows)
    if all_rows[0][0]==0:
        return render(request,'Demo3.html',{'dict1':[req['constituency']]})

    voter_id=req['voter']
    print(constituency_id)
    token=hashlib.sha1((voter_id+str(time.time())).encode()).hexdigest()
    token=token[:8].upper()
    print(token)
    stmt=f"Update user set otp='{token}' where voterid='{voter_id}'"
    print(stmt)
    cursor.execute(stmt)
    db.commit()
    db.close()
    logged_in=True
    return render(request, 'otp.html',{'dict1':[token]})

def otp_verify(request):
    global voter_id
    global logged_in
    global constituencyid
    print(logged_in)
    if(logged_in is False):
        return render(request,'Demo.html')
    req=request.GET
    db = sqlite3.connect('voter1.db')
    cursor = db.cursor()
    print('\n\n',req,'\n\n')
    cursor.execute(f"SELECT count(*) from user where voterid='{voter_id}' and otp='{req['otp']}'")
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
    blockchain = custom_blockchain.Blockchain()
    blockchain.load_stored_blockchain()
    verify_data=blockchain.is_chain_valid()
    if verify_data:
        blockchain.add_and_mine_block(voter_id,candidate)
        blockchain.update_stored_blockchain()
        db = sqlite3.connect('voter1.db')
        cursor = db.cursor()
        stmt=f"Update election set voted='1' where voterid='{voter_id}'"
        print(stmt)
        cursor.execute(stmt)
        db.commit()
    else:
        return render(request, 'Alert.html')
    logged_in=False
    voter_id=''
    candidates=[i['candidate'] for i in blockchain.chain]
    party=defaultdict(int)
    print(candidates)
    for i in candidates[1:]:
        stmt=f"select party from candidate where candidateid='{i}'"
        cursor.execute(stmt)
        all_rows = cursor.fetchall()
        party[all_rows[0][0]]+=1
    party_list=[i for i in party.items()]
    print(party_list)
    return render(request, 'thanks.html',{'dict1':blockchain.chain,'dict2':party_list})
