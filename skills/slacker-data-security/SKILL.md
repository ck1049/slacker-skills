---
name: slacker-data-security
description: >-
  Language-agnostic layered encryption playbook: business RSA + AES at rest (externalized keys),
  ephemeral transport RSA (memory-only) for client-to-server sensitive payloads, irreversible password
  hashing after transport decrypt, stable wire formats (RSA-OAEP-SHA256 chunking, AES-GCM with 12-byte IV),
  and stale-key signaling (e.g. HTTP/API code 4001). Use when designing or reviewing crypto for any stack
  (mobile, desktop, web service, embedded clients), adding sensitive PII fields, key bootstrap on startup,
  hybrid RSA+AES message bodies, or debugging post-restart decrypt failures. Triggers: 数据安全, 业务密钥,
  通信RSA, 客户端加密, transport public key, ENC$RSA$, ENC$AES$, OAEP 分段, Slacker data security,
  slacker-data-security.
---

# Slacker data security (language-agnostic)

## Instructions

Apply the model below in the **host language and crypto libraries** of the product. **Do not copy Java types or APIs** unless the stack is JVM; for Java/JVM stacks, read the labeled **Java 示例** under `references/`.

1. **Maintain two RSA roles plus one business symmetric key (AES-256-GCM recommended)**
   - **Business RSA / business AES**: long-lived keys for server-side storage; load from **configured paths** or a secrets manager; **generate and persist** if files are missing (first boot), with secure file permissions.
   - **Transport RSA**: **memory-only** key pair per process; **clients** (browser, mobile, desktop) fetch a fresh **public key** after deploy or restart via a dedicated endpoint or channel doc.

2. **At-rest encoding**
   - **Small sensitive scalars** (email, phone, address, reversible third-party secrets): encrypt with **business RSA**, store as an explicit prefix (e.g. `ENC$RSA$`) + Base64(ciphertext bytes). Chunk per RSA OAEP limits for the chosen modulus.
   - **Large text or blobs**: encrypt with **business AES-GCM** (or equivalent AEAD), store as prefix (e.g. `ENC$AES$`) + Base64(`IV || ciphertext+tag`). If legacy rows lack the prefix, treat as plaintext for read paths until migrated.

3. **Transport (client to server)**
   - Encrypt sensitive request parameters with the **transport RSA public key** using **RSA-OAEP with SHA-256** (or the same MGF1/OAEP parameters the server documents). Use the server-published **maximum plaintext chunk size** for segmentation; concatenate ciphertext blocks; then Base64 for JSON/binary-safe transport.
   - **Irreversible passwords**: client encrypts password with transport RSA → server decrypts to plaintext → apply **slow password hashing** (bcrypt, Argon2, scrypt, PBKDF2 with appropriate work factor) → store **only** the password hash. Never store transport-RSA ciphertext of the password in the user store.

4. **Stale transport key**
   - If transport decrypt fails (wrong padding, length mismatch after restart): return a **dedicated stable error code** (e.g. `4001`) and message so the **client** refetches the public key and retries.

5. **Wire format checklist (language-neutral)**

   - Publish from the server: PEM or SPKI for the transport public key, **modulus-related** `ciphertextBlockBytes`, and **oaepSha256MaxPlainChunkBytes** (or equivalent) so clients segment identically to the server.
   - **RSA**: UTF-8 bytes → chunks ≤ max chunk → RSA-OAEP-SHA256 per chunk → concatenate → Base64.
   - **AES-GCM**: random **12-byte IV**, 128-bit tag, output **`IV || (cipher+tag)`** then Base64.

6. **Multi-IDE installation**

   - Canonical skill repo: **`git@github.com:ck1049/slacker-skills.git`**（HTTPS: `https://github.com/ck1049/slacker-skills.git`）。完整 **clone + 复制到各 IDE** 的命令见 **[references/install-multi-ide.md](references/install-multi-ide.md)**（含 Bash / PowerShell、全局与项目级、Codex `install-skill-from-github.py`、可选 `npx skills` 与 sparse clone）。
   - 路径总览与免责声明仍见该文件中的「路径对照表」一节；各产品路径可能随版本变更，请以官方文档为准。

## References (read as needed)

- **[references/install-multi-ide.md](references/install-multi-ide.md)** — where to copy this skill folder per IDE (global vs project).
- **[references/bootstrap-java.md](references/bootstrap-java.md)** — **Java 示例**：Spring-style bootstrap, prefixes, exception mapping (reference only).
- **[references/embedded-utils-java.md](references/embedded-utils-java.md)** — **Java 示例**：JDK RSA/AES helper snapshots (reference only; prefer your language’s vetted crypto APIs).

Keep links **one level deep** from this `SKILL.md`.
