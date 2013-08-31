
from twisted.internet.defer import inlineCallbacks
from storm import exceptions

from globaleaks.tests import helpers

from globaleaks.settings import transact
from globaleaks.models import Receiver, User

class TestTransaction(helpers.TestGL):

    def test_transaction_with_exception(self):
        try:
            yield self._transaction_with_exception()
            self.assertTrue(False)
        except Exception:
            self.assertTrue(True)

    def test_transaction_ok(self):
        return self._transaction_ok()

    def test_transaction_with_commit_close(self):
        return self._transaction_with_commit_close()

    @inlineCallbacks
    def test_transact_with_stuff(self):
        receiver_id = yield self._transact_with_stuff()
        # now check data actually written
        store = transact.get_store()
        self.assertEqual(store.find(Receiver, Receiver.id == receiver_id).count(), 1)

    @inlineCallbacks
    def test_transact_with_stuff_failing(self):
        receiver_id = yield self._transact_with_stuff_failing()
        store = transact.get_store()
        self.assertEqual(list(store.find(Receiver, Receiver.id == receiver_id)), [])

    @inlineCallbacks
    def test_transact_decorate_function(self):
        @transact
        def transaction(store):
            self.assertTrue(getattr(store, 'find'))
        yield transaction()

    @transact
    def _transaction_with_exception(self, store):
        raise Exception

    #def transaction_with_exception_while_writing(self):
    @transact
    def _transaction_ok(self, store):
        self.assertTrue(getattr(store, 'find'))
        return

    @transact
    def _transaction_with_commit_close(self, store):
        store.commit()
        store.close()

    @transact
    def _transact_with_stuff(self, store):
        r = self.localization_set(self.dummyReceiver, Receiver, 'en')
        receiver_user = User(self.dummyReceiverUser)
        receiver_user.last_login = self.dummyReceiverUser['last_login']

        # Avoid receivers with the same username!
        receiver_user.username = unicode("xxx")

        store.add(receiver_user)
 
        receiver = Receiver(r)
        receiver.user_id = receiver_user.id
        receiver.gpg_key_status = Receiver._gpg_types[0] # this is a required field!
        receiver.notification_fields = self.dummyReceiver['notification_fields']
        store.add(receiver)

        return receiver.id

    @transact
    def _transact_with_stuff_failing(self, store):
        r = self.localization_set(self.dummyReceiver, Receiver, 'en')
        receiver_user = User(self.dummyReceiverUser)
        receiver_user.last_login = self.dummyReceiverUser['last_login']
        store.add(receiver_user)

        receiver = Receiver(r)
        receiver.user_id = receiver_user.id
        receiver.gpg_key_status = Receiver._gpg_types[0] # this is a required field!
        receiver.notification_fields = self.dummyReceiver['notification_fields']
        store.add(receiver)

        raise exceptions.DisconnectionError
