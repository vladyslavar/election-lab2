import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class VotingMachine:
    def __init__(self):
        self._votes = {}
        self._candidates = []

        self.known_IDs = []
        self.voted_IDs = []
        self._voting_results = {}

        _key_pair = RSA.generate(2048)
        self.pub_key = RSA.import_key(_key_pair.publickey().export_key("PEM"))
        self.__priv_key = RSA.import_key(_key_pair.exportKey("PEM"))

    def register_candidate(self, candidate):
        if candidate not in self._candidates:
            self._candidates.append(candidate)
            self._votes[candidate] = 0

    def get_candidates(self):
        return self._candidates
    
    def blind_bulletin_sign(self, voter_ID, pack, voter_private_key):
        if voter_ID not in self.known_IDs:
            pack_to_open = pack[:-1]
            pack_to_sign = pack[-1:]
            pack_to_send = []
            isWrongBulletin = False

            for sub_pack in pack_to_open:
                for bulletin in sub_pack:
                    decoded_bulletin = self.decode_RSA(bulletin, voter_private_key)
                    if not self.check_bulletin(decoded_bulletin):
                        isWrongBulletin = True
            # for vote in pack_to_open:
            #     bulletin = self.decode_RSA(vote, voter_private_key)

            #     if not self.check_bulletin(bulletin):
            #         isWrongBulletin = True

            if not isWrongBulletin:
                for sub_pack_to_sign in pack_to_sign:
                    for hiden_bulletin in sub_pack_to_sign:
                        signature = self.sign_bulletin(hiden_bulletin)
                        # content_with_signature = hiden_bulletin + "||" + signature
                        pack_to_send.append((hiden_bulletin, signature))
                    self.known_IDs.append(voter_ID)
                return pack_to_send

    
    def vote_consideration(self, voted_bulletin, voter_private_key):
        content, signature = voted_bulletin
        # content, signature = decoded_bulletin.split("||")
        decoded_bulletin = self.decode_RSA(content, self.__priv_key)

        if self.check_signature(decoded_bulletin, signature):
            decoded_bulletin = self.decode_RSA(decoded_bulletin, voter_private_key)
            if self.check_bulletin(decoded_bulletin):
                decoded_bulletin = decoded_bulletin.decode("utf-8")
                candidate, voter_ID = decoded_bulletin.split("|")
                if voter_ID not in self.voted_IDs:
                    self._votes[candidate] += 1
                    self.voted_IDs.append(voter_ID)
                    self._voting_results[voter_ID] = candidate
                    return True

    def get_voting_results(self):
        voting_results_count = {}
        for candidate in self._candidates:
            voting_results_count[candidate] = 0
        for voter_ID in self._voting_results:
            candidate = self._voting_results[voter_ID]
            voting_results_count[candidate] += 1
        return self._voting_results, voting_results_count


    def decode_RSA(self, encoded_massage, private_key):
        cipher = PKCS1_OAEP.new(private_key)
        decoded_message = cipher.decrypt(encoded_massage)
        
        return decoded_message
    
    def check_bulletin(self, bulletin):
        bulletin = bulletin.decode("utf-8")
        vote, voter_ID = bulletin.split("|")
        if vote in self._candidates:
            try:
                uuid.UUID(voter_ID)
            except:
                return False
            return True
        else:
            return False
        
    def sign_bulletin(self, bulletin):
        h = SHA256.new(bulletin)
        signature = pkcs1_15.new(self.__priv_key).sign(h)
        return signature
    
    def check_signature(self, bulletin, signature):
        h = SHA256.new(bulletin)
        try:
            pkcs1_15.new(self.pub_key).verify(h, signature)
            return True
        except:
            return False


APPROVED_VOTERS_FILE = "approved_voters.txt"
class provider_IDs:
    def __init__(self):
        self.voters = {}
        
    def define_IDs(self):
        file = open(APPROVED_VOTERS_FILE, "r")
        for line in file:
            line = line.split()[0]
            self.voters[line] = str(uuid.uuid4())
        file.close()

    def get_ID(self, passport):
        try:
            requested_id =self.voters[passport]
        except:
            return None
        return requested_id
    
    def get_all_IDs(self):
        return self.voters.values()
    

if __name__ == "__main__":
    ids = provider_IDs()
    ids.define_IDs()
    print()