# Java 示例：业务密钥引导 + 通信密钥 + 落库封装

> **范围**：以下文件名、注解与类名均为 **Java / Spring Boot 生态示例**，用于 Slacker Official 等 JVM 后端参考。**非 Java 项目请勿照搬类名与包路径**；仅复用「职责划分」与「数据流」概念，并用各自语言的加密库实现。

说明：以下为仓库中相关 Java 类的结构快照，便于复制到其它 JVM 项目；合并后请以编译通过与安全评审为准。

## Java 示例：`CryptoProperties`（`@ConfigurationProperties(prefix = "app.crypto")`）

绑定字段建议包含：

- `businessKeysDirectory`
- `businessRsaPublicFile` / `businessRsaPrivateFile` / `businessAesKeyFile`
- `businessRsaKeyBits`（2048/3072）
- `transportRsaKeyBits`（2048/3072）

## Java 示例：`BusinessCryptoKeyManager`（`@PostConstruct`）

逻辑要点：

1. `Paths.get(businessKeysDirectory).toAbsolutePath().normalize()` 并 `Files.createDirectories(dir)`
2. 若 `public`/`private` 任一缺失：生成 `RSAUtils.generateKeyPair(bits)` 并 `writePublicKeyPem` / `writePrivateKeyPem`
3. 若 AES 文件缺失：`AESUtils.generateKey()` + `writeKeyBase64`
4. 最后 `readPublicKeyPem` / `readPrivateKeyPem` / `readKeyBase64` 载入内存

落库前缀常量建议固定：

- `AT_REST_RSA_PREFIX = "ENC$RSA$"`
- `AT_REST_AES_PREFIX = "ENC$AES$"`

## Java 示例：`TransportRsaHolder`（构造器或 `@PostConstruct`）

- `RSAUtils.generateKeyPair(transportBits)` 仅保存 `KeyPair` 在内存
- 暴露 `getPublicKeyPem()`、`getCiphertextBlockBytes()`、`getOaepSha256MaxPlainChunkBytes()`（可用 `RSAUtils.rsaCipherBlockBytes` / `RSAUtils.maxOaepSha256PlaintextBytes`）

## Java 示例：`BusinessDataCrypto`

- `encryptRsaAtRest`：`RSAUtils.encrypt(utf8, businessPublic)` → `ENC$RSA$` + Base64
- `decryptRsaAtRest`：若无前缀则按明文历史数据原样返回
- `encryptAesAtRest` / `decryptAesAtRest`：同理使用 `ENC$AES$` 前缀

## Java 示例：`TransportPayloadCrypto`

- `decryptUtf8FromBase64` / `decryptBinaryFromBase64`：`Base64.decode` → `RSAUtils.decrypt`（通信私钥）
- `decryptLoginPasswordOrLegacyPlaintext`：若 Base64 解码后长度不是 `ciphertextBlockBytes` 的整数倍，则按明文兼容处理；否则尝试 RSA 解密；`BadPaddingException` 链路映射为 `TransportKeyMismatchException`

## Java 示例：`GlobalExceptionHandler`

- `TransportKeyMismatchException` → `ApiResponse.fail(ApiCodes.TRANSPORT_KEY_STALE, message)`

## Java 示例：仓库内权威路径（Slacker Official）

- `backend/src/main/java/com/slacker/official/util/RSAUtils.java`、`AESUtils.java`
- `backend/.../config/CryptoProperties.java`、`application.yml` → `app.crypto`
- `backend/.../crypto/BusinessCryptoKeyManager.java`、`TransportRsaHolder.java`、`TransportPayloadCrypto.java`、`BusinessDataCrypto.java`
- `backend/.../controller/CryptoController.java`
- 客户端参考实现（TypeScript / Web Crypto，**非 Java**）：`frontend/src/utils/transportCrypto.ts`、`admin/src/utils/transportCrypto.ts`
