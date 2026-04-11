# Java 示例：业务密钥引导 + 通信密钥 + 落库封装

> **范围**：以下文件名、注解与类名均为 **Java / Spring Boot 生态示例**，仅供 JVM 后端实现时对照。**非 Java 项目请勿照搬类名与包路径**；仅复用「职责划分」与「数据流」概念，并用各自语言的加密库实现。

说明：以下为常见模块划分的结构快照，便于迁移到其它 JVM 项目；落地时类名与包名请按本团队规范自定，合并后请以编译通过与安全评审为准。

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

## Java 示例：模块落位建议（路径自定）

实现时可按职责拆分为：**配置绑定**（如 `@ConfigurationProperties`）、**业务密钥引导**、**通信密钥持有者**、**落库加解密服务**、**公钥下发接口**、**统一异常映射**等；工具类（RSA/AES PEM 与分段加解密）宜放在独立 `util` 或 `crypto` 包。客户端侧（任意技术栈）需实现与服务端一致的 **OAEP 分段**与 **AES-GCM 报文布局**，勿在技能文档中绑定某一仓库的目录结构。
