# JECDH

JECDH is a small ECDH package that uses Py4J, so the front-end is written in Python, and the back-end is written in Java. Py4J utilizes an API-like interface, so for security reasons, this implementation should only be used on a secured, closed network. 

## Usage

### About the Java Backend

To get started, you need to be running the Py4J Gateway to listen for Python passing ECDH parameters. The default port the Gateway runs on is `25333`, and can be changed by starting the server manually, or by initializing the JECDH class with the `gateway_port` keyword argument. Upon initialization, the class polls the port it expects to find the backend running on, and if it doesn't get a response, to then start the backend on that port. 

```python
from jecdh import JECDH

# This starts on the default port number of 25333
ecdh = JECDH() 
# This starts on port 36999
ecdh = JECDH(gateway_port=36999)
```

Additionally, manually compiling and starting the backend from the `java` folder (on port `10888`) is also possible:

```console
javac -cp py4j.jar:bouncycastle.jar:bcprov-jdk18on-171.jar:. EllipticCurve.java
java -cp py4j.jar:bouncycastle.jar:bcprov-jdk18on-171.jar:. EllipticCurve 10888
```

#### Java Version Info: 

```
openjdk 17.0.1 2021-10-19
OpenJDK Runtime Environment Temurin-17.0.1+12 (build 17.0.1+12)
OpenJDK 64-Bit Server VM Temurin-17.0.1+12 (build 17.0.1+12, mixed mode, sharing)
```

### Usage and Examples

After importing and initializing the library, you must use the `set_private_key` and `set_public_key` functions to set to keys to use. Each of these functions kates a `key_type` kwarg. 



```python
from jecdh import JECDH

private_keystore_pkcs12 = open("<file>", "rb").read()
private_key_pem = open("<file>", "rb").read()
private_pkcs8 = open("<file>", "rb").read()
public_key_ephemeral = open("<file>", "rb").read()
public_key_x509 = open("<file>", "rb").read()

ecdh = JECDH()

# Reading a Private Key from an Encrypted PKCS12 Keystore and a public key in X509
ecdh.set_private_key(private_keystore_pkcs12, key_type="PKCS12", passwd="passwerd")
ecdh.set_public_key(public_key_x509, "X509")
shared_secret = ecdh.exchange()

# Reading a Private Key from a PKCS8 file and a public key in X509
ecdh.set_private_key(private_pkcs8, key_type="PKCS8")
ecdh.set_public_key(public_key_x509, key_type="X509")
shared_secret = ecdh.exchange()

# Reading a Private Key from a PEM file
# NOTE: If your PEM file does not work with PKCS8, it 
# may be in SEC1, which this format handles. 
ecdh.set_private_key(private_key_pem, key_type="PEM")
ecdh.set_public_key(public_key_ephemeral, "X509")
shared_secret = ecdh.exchange()

# do stuff with shared secret below
```

## TODO
* Add compressed/uncompressed points (Ask ChatGPT what the difference between these are?)
