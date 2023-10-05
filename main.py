from voting_machine_client import VotingMachineClient
from voting_machine import VotingMachine, provider_IDs

candidates = ["Donald Trump", "Joe Biden", "Kanye West", "Mickey Mouse"]
voting_machine = VotingMachine()
ID_provider = provider_IDs()

def immitate_voting(passport):
    client = VotingMachineClient(passport, voting_machine, ID_provider)
    if client.ID == None:
        return False
    print("passport: " + passport + ". Your ID: " + client.ID)
    pack = client.form_bulletin_pack()

    pack_to_vote = voting_machine.blind_bulletin_sign(client.ID, pack, client.private_key)
    if check_if_error(pack_to_vote):
        return False

    voted_bulletin = client.vote(pack_to_vote)
    if check_if_error(voted_bulletin):
        return False
    
    ifVoted = voting_machine.vote_consideration(voted_bulletin, client.private_key)
    if check_if_error(ifVoted):
        return False
    return ifVoted

def check_if_error(data):
    if isinstance(data, str):
        print(data)
        return True
    return False

if __name__ == "__main__":
    ID_provider.define_IDs()
    for candidate in candidates:
        voting_machine.register_candidate(candidate)

    passports = ["11111", "5243189076", "5243189076", "8079615423", "3628901574", "5014786329", "8947236105", "2054983176", "6354728901"]
    # passports = ["5243189076"]
    for passport in passports:
        ifVoted = immitate_voting(passport)
        if ifVoted:
            print("Voted")
        else:
            print("Not voted")
    votings, counts = voting_machine.get_voting_results()
    print("All votes:")
    for vote in votings:
        print(vote + " - " + str(votings[vote]))
    print("Voting results:")
    print(counts)
