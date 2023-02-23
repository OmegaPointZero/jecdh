import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.security.*;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Enumeration;
import javax.crypto.KeyAgreement;

import org.bouncycastle.openssl.PEMKeyPair;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;

import py4j.GatewayServer;


public class EllipticCurve {

    public static byte[] key_exchange(Object privateKeyStr,
                                String privateKeyType,
                                byte[] publicKeyStr,
                                String publicKeyType,
                                String privatePass) throws Exception {

        byte[] privateKeyBytes = null;
        String privateKeyString = null;

        if (privateKeyStr instanceof byte[]){
            privateKeyBytes = (byte[]) privateKeyStr;
        } else if (privateKeyStr instanceof String){
            privateKeyString = (String) privateKeyStr;
        }

        PrivateKey privateKey = null;
        PublicKey publicKey = null;

        switch (privateKeyType){
            case "PKCS8":
                privateKey = loadPrivateKeyPKCS8(privateKeyBytes);
                break;
            case "PEM":
                privateKey = loadPrivateKeySEC1(privateKeyString);
                break;
            case "PKCS12":
                privateKey = loadPrivateKeyPKCS12(privateKeyBytes, privatePass.toCharArray());
                break;
        }

        switch (publicKeyType){
            case "X509":
                publicKey = loadPublicKeyX509(publicKeyStr);
        }

        byte[] bytes = ellipticCurveDHExchange(privateKey, publicKey);
        return bytes;
    }

    private static byte[] ellipticCurveDHExchange(PrivateKey privateKey, PublicKey publicKey)
            throws NoSuchAlgorithmException, InvalidKeyException {
        KeyAgreement ka = KeyAgreement.getInstance("ECDH");
        ka.init(privateKey);
        ka.doPhase(publicKey, true);
        return ka.generateSecret();
    }


    private static PrivateKey loadPrivateKeyPKCS8(byte[] privateKey) throws Exception {
        PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(privateKey);
        KeyFactory kf = KeyFactory.getInstance("EC");
        return kf.generatePrivate(spec);
    }

    private static PrivateKey loadPrivateKeySEC1(String pem) throws Exception {
        final PEMParser pemParser = new PEMParser(new StringReader(pem));
        final Object parsedPem = pemParser.readObject();
        if (!(parsedPem instanceof PEMKeyPair)) {
            throw new IOException("Attempted to parse PEM string as a keypair, but it's actually a " + parsedPem.getClass());
        }
        final JcaPEMKeyConverter converter = new JcaPEMKeyConverter();

        return converter.getKeyPair((PEMKeyPair) parsedPem).getPrivate();
    }

    private static PrivateKey loadPrivateKeyPKCS12(byte[] pk, char[] password) throws Exception {
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        InputStream inputStream = new ByteArrayInputStream(pk);
        keyStore.load(inputStream, password);
        Enumeration<String> aliases = keyStore.aliases();
        PrivateKey privateKey = null;
        while (aliases.hasMoreElements()) {
            String alias = aliases.nextElement();
            try {
                privateKey = (PrivateKey) keyStore.getKey(alias, password);
                return privateKey;
            } catch(Exception e){
                continue;
            }
        }
        return privateKey;
    }

    private static PublicKey loadPublicKeyX509(byte[] pubKey) throws Exception {
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(pubKey);
        KeyFactory kf = KeyFactory.getInstance("EC");
        return kf.generatePublic(keySpec);
    }
    public static void main(String[] args) {
        EllipticCurve app = new EllipticCurve();
        int portNumber;
        if (args.length == 1) {
            portNumber = Integer.parseInt(args[0]);
        } else {
            portNumber = 25333;
        }
        // app is now the gateway.entry_point
        GatewayServer server = new GatewayServer(app, portNumber);
        server.start();
    }
}