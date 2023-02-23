import os
import base64
import unittest

from jecdh import JECDH


# Declaring this all in the __init__ function was giving me problems
# Since it is overrriding the unittest init function, So I'm just doing
# it here. Will probably fix this in the future.
def get_file(filename):
    current_directory = os.getcwd()
    prefix = current_directory + "/test_fixtures/"
    f = open(prefix + filename, "rb")
    key = f.read()
    f.close()
    return key


private_pkcs8 = get_file("private_pkcs8")
private_keystore_pkcs12 = get_file("private_keystore_pkcs12")
private_key_pem = get_file("private_key_pem")
public_key_ephemeral = get_file("public_key_ephemeral")
new_public_key = get_file("new_public_key")


class TestECDH(unittest.TestCase):

    def test_no_public(self):
        ecdh = JECDH()
        ecdh.set_private_key(private_pkcs8, key_type="PKCS8")
        with self.assertRaisesRegex(Exception, "Error: No public key set."):
            ecdh.exchange()

    def test_no_private(self):
        ecdh = JECDH()
        ecdh.set_public_key(new_public_key, key_type="X509")
        with self.assertRaisesRegex(Exception, "Error: No private key set."):
            ecdh.exchange()

    def test_no_public_type(self):
        ecdh = JECDH()
        with self.assertRaisesRegex(Exception, "Unsupported public key type: SomethingWrong.*"):
            ecdh.set_public_key(new_public_key, key_type="SomethingWrong")

    def test_no_private_type(self):
        ecdh = JECDH()
        # Make sure you open the keys as bytes, not strings
        with self.assertRaisesRegex(Exception, "Unsupported private key type: SomethingWrong."):
            ecdh.set_private_key(private_pkcs8, key_type="SomethingWrong")

    def test_generated_keypair(self):
        ecdh = JECDH()
        # Make sure you open the keys as bytes, not strings
        ecdh.set_private_key(private_pkcs8, key_type="PKCS8")
        ecdh.set_public_key(new_public_key, key_type="X509")
        shared_secret = base64.b64encode(ecdh.exchange())
        expected = b"9/mnqq+gMfEbBiKX+pvzat+aCFLvn415Ez4NGbzLUHM="
        self.assertEqual(shared_secret, expected)

    def test_apple_pay_keypair(self):
        ecdh = JECDH()
        ecdh.set_private_key(private_key_pem, key_type="PEM")
        ecdh.set_public_key(public_key_ephemeral, "X509")
        shared_secret = ecdh.exchange()
        expected = b"a2pPfemSdA560FnzLSv8zfdlWdGJTonApOLq1zfgx8w="
        self.assertEqual(base64.b64encode(shared_secret), expected)

    def test_pkcs12_keypair(self):
        ecdh = JECDH()
        ecdh.set_private_key(private_keystore_pkcs12, key_type="PKCS12", passwd="super_secure_password")
        ecdh.set_public_key(new_public_key, "X509")
        shared_secret = ecdh.exchange()
        expected = b"XQwhaAQjC3bgXPcy3nkrZE9NSs+8UwcYe9kM0cfP8Ck="
        self.assertEqual(base64.b64encode(shared_secret), expected)


if __name__ == "__main__":
    unittest.main()
