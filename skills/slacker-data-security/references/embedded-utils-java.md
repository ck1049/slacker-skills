# Java 示例：嵌入式 JDK 工具类快照（RSAUtils / AESUtils）

## 目录

- Java 示例：RSAUtils.java（见下文代码块；精简快照）
- Java 示例：AESUtils.java（见下文代码块；精简快照）

> **非 Java 项目请勿直接复制以下代码**；请用目标语言的标准库或经审计的加密库实现等价行为（OAEP-SHA256 分段、AES-GCM IV+tag 布局等）。
>
> 来源：`backend/src/main/java/com/slacker/official/util/`（Slacker Official 仓库）。若与仓库冲突，以仓库为准。本文件较长，优先在仓库中阅读权威源码；此处用于 JVM 离线搬运。

## Java 示例：RSAUtils.java

```java
package com.slacker.official.util;

import javax.crypto.Cipher;
import javax.crypto.spec.OAEPParameterSpec;
import javax.crypto.spec.PSource;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.*;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.MGF1ParameterSpec;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

public final class RSAUtils {

    private RSAUtils() {}

    public static final String ALGO_RSA = "RSA";
    public static final String TRANSFORMATION_OAEP_SHA256 = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding";
    public static final String TRANSFORMATION_OAEP_SHA1 = "RSA/ECB/OAEPWithSHA-1AndMGF1Padding";

    private static final String PEM_BEGIN_PRIVATE = "-----BEGIN PRIVATE KEY-----";
    private static final String PEM_END_PRIVATE = "-----END PRIVATE KEY-----";
    private static final String PEM_BEGIN_PUBLIC = "-----BEGIN PUBLIC KEY-----";
    private static final String PEM_END_PUBLIC = "-----END PUBLIC KEY-----";

    public static KeyPair generateKeyPair(int keySize) {
        if (keySize < 2048) {
            throw new IllegalArgumentException("RSA keySize must be >= 2048 bits");
        }
        try {
            KeyPairGenerator kpg = KeyPairGenerator.getInstance(ALGO_RSA);
            SecureRandom sr = getStrongSecureRandom();
            kpg.initialize(keySize, sr);
            return kpg.generateKeyPair();
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("Failed to generate RSA key pair", e);
        }
    }

    public static KeyPair generateKeyPair() {
        return generateKeyPair(3072);
    }

    public static byte[] encrypt(byte[] data, PublicKey publicKey) {
        return encrypt(data, publicKey, MGF1ParameterSpec.SHA256);
    }

    public static byte[] encrypt(byte[] data, PublicKey publicKey, MGF1ParameterSpec mgf1Hash) {
        try {
            Cipher cipher = getOaepCipher(Cipher.ENCRYPT_MODE, publicKey, mgf1Hash);
            int maxBlock = getMaxOaepInputLen((RSAPublicKey) publicKey, mgf1Hash);
            return processBlocks(data, cipher, maxBlock);
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("RSA encrypt failed", e);
        }
    }

    public static byte[] decrypt(byte[] cipherBytes, PrivateKey privateKey) {
        return decrypt(cipherBytes, privateKey, MGF1ParameterSpec.SHA256);
    }

    public static byte[] decrypt(byte[] cipherBytes, PrivateKey privateKey, MGF1ParameterSpec mgf1Hash) {
        try {
            Cipher cipher = getOaepCipher(Cipher.DECRYPT_MODE, privateKey, mgf1Hash);
            int blockSize = ((RSAPrivateKey) privateKey).getModulus().bitLength() / 8;
            return processBlocks(cipherBytes, cipher, blockSize);
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("RSA decrypt failed", e);
        }
    }

    public static String toPem(PublicKey publicKey) {
        String base64 = Base64.getMimeEncoder(64, new byte[]{'\n'}).encodeToString(publicKey.getEncoded());
        return PEM_BEGIN_PUBLIC + "\n" + base64 + "\n" + PEM_END_PUBLIC + "\n";
    }

    public static String toPem(PrivateKey privateKey) {
        String base64 = Base64.getMimeEncoder(64, new byte[]{'\n'}).encodeToString(privateKey.getEncoded());
        return PEM_BEGIN_PRIVATE + "\n" + base64 + "\n" + PEM_END_PRIVATE + "\n";
    }

    public static void writePublicKeyPem(PublicKey publicKey, Path path) throws IOException {
        Files.writeString(path, toPem(publicKey), StandardCharsets.US_ASCII);
    }

    public static void writePrivateKeyPem(PrivateKey privateKey, Path path) throws IOException {
        Files.writeString(path, toPem(privateKey), StandardCharsets.US_ASCII);
    }

    public static PublicKey readPublicKeyPem(Path path) {
        try {
            String pem = Files.readString(path, StandardCharsets.US_ASCII);
            return readPublicKeyPem(pem);
        } catch (IOException e) {
            throw new RuntimeException("Read public key PEM failed", e);
        }
    }

    public static PublicKey readPublicKeyPem(String pem) {
        try {
            String base64 = stripPem(pem, PEM_BEGIN_PUBLIC, PEM_END_PUBLIC);
            byte[] der = Base64.getMimeDecoder().decode(base64);
            X509EncodedKeySpec spec = new X509EncodedKeySpec(der);
            KeyFactory kf = KeyFactory.getInstance(ALGO_RSA);
            return kf.generatePublic(spec);
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("Parse public key PEM failed", e);
        }
    }

    public static PrivateKey readPrivateKeyPem(Path path) {
        try {
            String pem = Files.readString(path, StandardCharsets.US_ASCII);
            return readPrivateKeyPem(pem);
        } catch (IOException e) {
            throw new RuntimeException("Read private key PEM failed", e);
        }
    }

    public static PrivateKey readPrivateKeyPem(String pem) {
        try {
            if (pem.contains("BEGIN RSA PRIVATE KEY")) {
                throw new IllegalArgumentException("PKCS#1 RSA PRIVATE KEY is not supported. Convert to PKCS#8.");
            }
            String base64 = stripPem(pem, PEM_BEGIN_PRIVATE, PEM_END_PRIVATE);
            byte[] der = Base64.getMimeDecoder().decode(base64);
            PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(der);
            KeyFactory kf = KeyFactory.getInstance(ALGO_RSA);
            return kf.generatePrivate(spec);
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("Parse private key PEM failed", e);
        }
    }

    public static String base64Encode(byte[] bytes) {
        return Base64.getEncoder().encodeToString(bytes);
    }

    public static byte[] base64Decode(String base64) {
        return Base64.getDecoder().decode(base64);
    }

    private static SecureRandom getStrongSecureRandom() {
        try {
            return SecureRandom.getInstanceStrong();
        } catch (NoSuchAlgorithmException e) {
            return new SecureRandom();
        }
    }

    private static Cipher getOaepCipher(int mode, Key key, MGF1ParameterSpec mgf1Spec) throws GeneralSecurityException {
        String transformation = (mgf1Spec == MGF1ParameterSpec.SHA256) ? TRANSFORMATION_OAEP_SHA256 : TRANSFORMATION_OAEP_SHA1;
        Cipher cipher = Cipher.getInstance(transformation);
        OAEPParameterSpec oaep = new OAEPParameterSpec(
                mgf1Spec.getDigestAlgorithm(),
                "MGF1",
                mgf1Spec,
                PSource.PSpecified.DEFAULT
        );
        cipher.init(mode, key, oaep);
        return cipher;
    }

    private static byte[] processBlocks(byte[] input, Cipher cipher, int maxBlock) throws GeneralSecurityException {
        if (input.length <= maxBlock) {
            return cipher.doFinal(input);
        }
        List<byte[]> parts = new ArrayList<>();
        int offset = 0;
        while (offset < input.length) {
            int len = Math.min(maxBlock, input.length - offset);
            byte[] chunk = cipher.doFinal(input, offset, len);
            parts.add(chunk);
            offset += len;
        }
        int total = parts.stream().mapToInt(a -> a.length).sum();
        byte[] out = new byte[total];
        int pos = 0;
        for (byte[] p : parts) {
            System.arraycopy(p, 0, out, pos, p.length);
            pos += p.length;
        }
        return out;
    }

    private static int getMaxOaepInputLen(RSAPublicKey publicKey, MGF1ParameterSpec mgf1Spec) {
        int k = publicKey.getModulus().bitLength() / 8;
        int hLen = hashLen(mgf1Spec);
        return k - 2 * hLen - 2;
    }

    public static int maxOaepSha256PlaintextBytes(PublicKey publicKey) {
        return getMaxOaepInputLen((RSAPublicKey) publicKey, MGF1ParameterSpec.SHA256);
    }

    public static int rsaCipherBlockBytes(PublicKey publicKey) {
        return ((RSAPublicKey) publicKey).getModulus().bitLength() / 8;
    }

    private static int hashLen(MGF1ParameterSpec mgf1Spec) {
        String algo = mgf1Spec.getDigestAlgorithm().toUpperCase();
        return switch (algo) {
            case "SHA-1" -> 20;
            case "SHA-256" -> 32;
            case "SHA-384" -> 48;
            case "SHA-512" -> 64;
            default -> 32;
        };
    }

    private static String stripPem(String pem, String begin, String end) {
        String trimmed = pem.trim();
        int s = trimmed.indexOf(begin);
        int e = trimmed.indexOf(end);
        if (s < 0 || e < 0 || e <= s) {
            throw new IllegalArgumentException("Invalid PEM format: missing header/footer");
        }
        String body = trimmed.substring(s + begin.length(), e);
        return body.replaceAll("\\s", "");
    }
}
```

## Java 示例：AESUtils.java

```java
package com.slacker.official.util;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.Objects;

public final class AESUtils {

    private AESUtils() {}

    public static final String ALGO_AES = "AES";
    public static final String TRANSFORMATION_GCM = "AES/GCM/NoPadding";
    public static final int IV_LENGTH_BYTES = 12;
    public static final int TAG_LENGTH_BITS = 128;

    public static SecretKey generateKey(int bits) {
        if (bits != 128 && bits != 192 && bits != 256) {
            throw new IllegalArgumentException("AES key size must be 128, 192, or 256 bits");
        }
        try {
            KeyGenerator kg = KeyGenerator.getInstance(ALGO_AES);
            kg.init(bits, getStrongSecureRandom());
            return kg.generateKey();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Failed to generate AES key", e);
        }
    }

    public static SecretKey generateKey() {
        return generateKey(256);
    }

    public static byte[] encrypt(byte[] plaintext, SecretKey key) {
        return encrypt(plaintext, key, null, TAG_LENGTH_BITS);
    }

    public static byte[] encrypt(byte[] plaintext, SecretKey key, byte[] aad, int tagBits) {
        Objects.requireNonNull(plaintext, "plaintext");
        Objects.requireNonNull(key, "key");
        if (tagBits % 8 != 0 || tagBits < 96 || tagBits > 128) {
            throw new IllegalArgumentException("GCM tagBits must be 96..128 and multiple of 8");
        }
        try {
            byte[] iv = new byte[IV_LENGTH_BYTES];
            getStrongSecureRandom().nextBytes(iv);
            GCMParameterSpec spec = new GCMParameterSpec(tagBits, iv);
            Cipher cipher = Cipher.getInstance(TRANSFORMATION_GCM);
            cipher.init(Cipher.ENCRYPT_MODE, key, spec);
            if (aad != null && aad.length > 0) {
                cipher.updateAAD(aad);
            }
            byte[] ciphertext = cipher.doFinal(plaintext);
            byte[] out = new byte[IV_LENGTH_BYTES + ciphertext.length];
            System.arraycopy(iv, 0, out, 0, IV_LENGTH_BYTES);
            System.arraycopy(ciphertext, 0, out, IV_LENGTH_BYTES, ciphertext.length);
            return out;
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("AES-GCM encrypt failed", e);
        }
    }

    public static byte[] decrypt(byte[] combined, SecretKey key) {
        return decrypt(combined, key, null, TAG_LENGTH_BITS);
    }

    public static byte[] decrypt(byte[] combined, SecretKey key, byte[] aad, int tagBits) {
        Objects.requireNonNull(combined, "combined");
        Objects.requireNonNull(key, "key");
        if (combined.length < IV_LENGTH_BYTES + 16) {
            throw new IllegalArgumentException("Invalid AES-GCM input: too short");
        }
        if (tagBits % 8 != 0 || tagBits < 96 || tagBits > 128) {
            throw new IllegalArgumentException("GCM tagBits must be 96..128 and multiple of 8");
        }
        try {
            byte[] iv = new byte[IV_LENGTH_BYTES];
            System.arraycopy(combined, 0, iv, 0, IV_LENGTH_BYTES);
            byte[] cipherAndTag = new byte[combined.length - IV_LENGTH_BYTES];
            System.arraycopy(combined, IV_LENGTH_BYTES, cipherAndTag, 0, cipherAndTag.length);

            GCMParameterSpec spec = new GCMParameterSpec(tagBits, iv);
            Cipher cipher = Cipher.getInstance(TRANSFORMATION_GCM);
            cipher.init(Cipher.DECRYPT_MODE, key, spec);
            if (aad != null && aad.length > 0) {
                cipher.updateAAD(aad);
            }
            return cipher.doFinal(cipherAndTag);
        } catch (GeneralSecurityException e) {
            throw new RuntimeException("AES-GCM decrypt failed", e);
        }
    }

    public static void writeKeyBase64(SecretKey key, Path path) throws IOException {
        String b64 = Base64.getEncoder().encodeToString(key.getEncoded());
        Files.writeString(path, b64, StandardCharsets.US_ASCII);
    }

    public static SecretKey readKeyBase64(Path path) throws IOException {
        String b64 = Files.readString(path, StandardCharsets.US_ASCII).trim();
        byte[] keyBytes = Base64.getDecoder().decode(b64);
        return new SecretKeySpec(keyBytes, ALGO_AES);
    }

    private static SecureRandom getStrongSecureRandom() {
        try {
            return SecureRandom.getInstanceStrong();
        } catch (NoSuchAlgorithmException e) {
            return new SecureRandom();
        }
    }
}
```
