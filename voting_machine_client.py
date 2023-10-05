from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random

NUMBER_OF_PACKS = 10

class VotingMachineClient:
    def __init__(self, passport, voting_machine, ID_provider):
        self.vm = voting_machine
        self.ID_provider = ID_provider

        self.passport = passport
        self.ID = None
        self.get_my_ID()

    def get_my_ID(self):
        self.ID = self.ID_provider.get_ID(self.passport)
        if self.ID == None:
            print("passport: " + self.passport +" You are not allowed to vote")
        else:
            return self.ID

    def form_bulletin_pack(self):
        candidates = self.vm.get_candidates()
        pack = []
        for i in range(NUMBER_OF_PACKS):
            sub_pack = []
            for candidate in candidates:
                content = candidate + "|"  + self.ID
                sub_pack.append(content)
            pack.append(sub_pack)
        encoded_pack = self.encode_pack(pack)
        return encoded_pack

    def vote(self, pack_to_vote):
        decoded_pack = []
        for item in pack_to_vote:
            bulletin, signature = item
            decoded_bulletin = self.decode_pack(bulletin)
            decoded_pack.append((decoded_bulletin, signature))

        # this will be manual action on real voting machine
        number_of_candidate =random.randint(0, len(decoded_pack) - 1)
        # number_of_candidate = len(decoded_pack) + 1
        if number_of_candidate >= len(decoded_pack):
            return "Wrong bulletin"
        chosen_candidate, sign = pack_to_vote[number_of_candidate]

        chipher = PKCS1_OAEP.new(self.vm.pub_key)
        if not isinstance(chosen_candidate, bytes):
            chosen_candidate = chosen_candidate.encode("utf-8")
        encoded_candidate = chipher.encrypt(chosen_candidate)
        result = (encoded_candidate, sign)
        return result
    

    def encode_pack(self, pack):
        encoded_pack = []

        keys = RSA.generate(1024)
        self.public_key = RSA.import_key(keys.publickey().export_key("PEM"))
        self.private_key = RSA.import_key(keys.exportKey("PEM"))

        cipher = PKCS1_OAEP.new(self.public_key)
        for sub_pack in pack:
            encoded_sub_pack = []
            for vote in sub_pack:
                if not isinstance(vote, bytes):
                    vote = vote.encode("utf-8")
                encoded_vote = cipher.encrypt(vote)
                encoded_sub_pack.append(encoded_vote)
            encoded_pack.append(encoded_sub_pack)

        return encoded_pack
    
    def decode_pack(self, encoded_bulletin):
        cipher = PKCS1_OAEP.new(self.private_key)
        decoded_bulletin = cipher.decrypt(encoded_bulletin)

        return decoded_bulletin.decode("utf-8")
