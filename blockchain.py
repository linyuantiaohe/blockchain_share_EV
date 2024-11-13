import hashlib
import json
import datetime

class Blockchain:
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.create_block(block_type='Start',business_message='0',proof=1, previous_hash='0')

    #The time format is "%Y-%m-%d %H:%M" for strat time and end time
    #Four business type: 'SN' for just share my charging-pile without need an exchange parking lot, 'SE' for share my charging-pile and need an exchange parking lot, 'BN' for just rent a charging-pile without an exchange parking lot, 'BE' for rent a charging-pile with an exchange parking lot
    def add_agent_business_message(self,business_type,myid,mylotid,starttime,endtime,price):
        new_agent_business_message='%s|%s|%s|%s|%s|%s'%(business_type,myid,mylotid,starttime,endtime,price)
        return new_agent_business_message

    #Two business type: 'N' for just share a charging-pile without need an exchange parking lot, 'E' for share a charging-pile with an exchange parking lot
    def add_deal_business_message(self,business_type,from_block_index,to_block_index,fromlotid,tolotid,starttime,endtime,price):
        new_deal_business_message='%s|%s|%s|%s|%s|%s|%s|%s'%(business_type,from_block_index,to_block_index,fromlotid,tolotid,starttime,endtime,price)
        return new_deal_business_message

    # This function is created
    # to add further blocks
    # into the chain
    # block_type is 'Agent' or 'Deal'
    def create_block(self, block_type, business_message, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'block_type':block_type,
                 'business_message':business_message,
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    # This function is created
    # to display the previous block
    def print_previous_block(self):
        return self.chain[-1]

    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1

        return True

    def chain_check_have_a_deal(self, agent_business_message):
        previous_block = self.chain[0]
        block_index = 1
        a_business_type,a_myid,a_mylotid,a_starttime,a_endtime,a_price=agent_business_message.split('|')
        target_business_type={'SN':['BN','BE'],'SE':['BE'],'BN':['SN'],'BE':['SN','SE']}[a_business_type]

        available_block_index={}
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block['block_type']=='Agent':
                b_business_type,b_myid,b_mylotid,b_starttime,b_endtime,b_price=block['business_message'].split('|')
                if b_business_type in target_business_type:
                    if datetime.datetime.strptime(b_starttime, "%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(a_endtime, "%Y-%m-%d %H:%M:%S") and datetime.datetime.strptime(b_endtime, "%Y-%m-%d %H:%M:%S")>datetime.datetime.strptime(a_starttime, "%Y-%m-%d %H:%M:%S"):
                        available_block_index[block_index]=True
            if block['block_type']=='Deal':
                c_business_type,c_from_block_index,c_to_block_index,c_fromlotid,c_tolotid,c_starttime,c_endtime,c_price=block['business_message'].split('|')
                if a_business_type[0]=='S' and c_to_block_index in available_block_index.keys():
                    available_block_index[block_index]=False
                elif a_business_type[0]=='B' and c_from_block_index in available_block_index.keys():
                    available_block_index[block_index]=False
            block_index+=1

        final_available=[]
        for i in available_block_index.keys():
            if available_block_index[i]:
                final_available.append(i)
        return final_available

    def make_a_deal(self,business_type,from_block_index,to_block_index,fromlotid,tolotid,starttime,endtime,price):
        previous_block = self.print_previous_block()
        previous_proof = previous_block['proof']
        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)
        deal_business_message=self.add_deal_business_message(business_type,from_block_index,to_block_index,fromlotid,tolotid,starttime,endtime,price)
        block=self.create_block('Deal',deal_business_message,proof,previous_hash)

        if business_type == 'E':
            message_for_share='Your charging pile will be used during %s to %s, and you can park your car at %s parking lot. You will get %s Yuan.'%(starttime,endtime,tolotid,price)
            message_for_rent='You can charge your EV at %s parking lot during %s to %s, and you need to pay %s Yuan. Please ensure your %d parking lot available as exchange.'%(fromlotid,starttime,endtime,price,tolotid)
        else:
            message_for_share='Your charging pile will be used during %s to %s. You will get %s Yuan.'%(starttime,endtime,price)
            message_for_rent='You can charge your EV at %s parking lot during %s to %s, and you need to pay %s Yuan.'%(fromlotid,starttime,endtime,price)
        return message_for_share,message_for_rent

    def make_a_request(self,agent_business_message):
        previous_block = self.print_previous_block()
        previous_proof = previous_block['proof']
        proof = self.proof_of_work(previous_proof)
        previous_hash = self.hash(previous_block)
        block=self.create_block('Agent',agent_business_message,proof,previous_hash)

    def get_available_list(self,agent_business_message):
        final_available = self.chain_check_have_a_deal(agent_business_message)
        return len(final_available)>0,final_available