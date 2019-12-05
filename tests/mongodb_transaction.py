"""
This example uses the new callback API for working with transactions, which starts a transaction, executes the specified
operations, and commits. The new callback api also incorporates retry logic for transientTransactionError or UnkownTransactionCommitResult
commit errors.
"""

from pymongo import MongoClient
from pymongo import WriteConcern
from pymongo import ReadPreference
import pymongo

urlstring = "mongodb://localhost:27017"

client = MongoClient(urlstring)
my_write_concern_majority = WriteConcern('majority',wtimeout=1000)
# Prereq: Create collections, CRUD operations in transactions must be on existing collection

client.get_database('inmotion', write_concern=my_write_concern_majority, ).clickstream.insert_one({'abc': 0})
client.get_database('test', write_concern=my_write_concern_majority).test.insert_one({'xyz': 0})


# step1: Define the callback that specifies the sequence of opetations to perform inside
def callback(my_session):
    collection_one = my_session.client.inmotion.clickstream
    collection_two = my_session.client.test.test
    # important: you must pass the session to the operations
    collection_one.insert_one({'abc': 1}, session=my_session)
    collection_two.insert_one({'xyz': 999}, session=my_session)



"""
This MongoDB deployment does not support retryable writes
"""

# step2: Start a client session
with client.start_session() as session:
    # step3: use with_transaction to start a transaction, execute the callback, and commit
    # the read concern: the read concern level specifies the level of isolation for read operations. for example, a read operation using a read
    # concern level of majority will return data  that has been written to majority of nodes.
    session.with_transaction(callback, pymongo.read_concern.ReadConcern('majority'),
                             write_concern=my_write_concern_majority,
                             read_preference=pymongo.read_preferences.ReadPreference.PRIMARY)
