# Docker Network TLS Debug Log — Arithmetica SaaS

## 1. Context

This document captures the troubleshooting performed for Docker image pull failures observed during local development.

Issue was isolated to Docker network behavior and does not impact application code.

---

## 2. Problem Observed

Running:

    docker run hello-world

Resulted in:

    failed size validation: 4660 != 562
    unexpected EOF

Docker was unable to successfully pull and validate image layers.

---

## 3. Environment Verification

The following checks were performed to rule out local system issues:

- Docker Desktop reinstalled
- Docker Engine verified running
- Disk space verified (~240GB free)
- CPU and memory resources verified
- Docker Desktop reset to factory defaults
- Network connectivity verified
- curl test to registry endpoint successful

Example:

    curl https://registry-1.docker.io/v2/

Result:
- Successful TLS handshake
- Registry responded correctly

---

## 4. Key Finding

Inspection of TLS certificate chain revealed:

    Issuer: CN=Groww-Decryption-ECDSA

This confirms that outbound HTTPS traffic is being intercepted and re-signed by a corporate TLS inspection proxy.

---

## 5. Root Cause Analysis

Docker image pulls operate as follows:

1. Image layers are downloaded over HTTPS.
2. Each layer is validated against a SHA256 digest.
3. Content length and integrity must match exactly.

Because corporate TLS inspection is decrypting and re-encrypting traffic:

- Payload may be buffered or re-chunked
- Streamed data may be modified
- Chunked encoding may be altered
- Connection may close prematurely

This results in:

- Content length mismatch
- SHA256 digest mismatch
- `failed size validation`
- `unexpected EOF`

Docker enforces strict content integrity and aborts the pull when validation fails.

This is not a Docker installation issue.
This is not a disk or system resource issue.

It is a network-layer payload integrity issue caused by TLS interception.

---

## 6. Why curl Works but Docker Fails

`curl` tests succeed because:

- They validate connection and handshake only
- Small payload
- No streamed layer validation

Docker fails because:

- It downloads large streamed image layers
- It performs strict content hash verification
- Any byte-level difference causes failure

---

## 7. Recommended Remediation

### Option A (Preferred — Enterprise Clean Fix)

Bypass TLS inspection for:

- registry-1.docker.io
- auth.docker.io
- production.cloudflare.docker.com
- index.docker.io

Traffic to these domains should not be decrypted or modified.

---

### Option B (Enterprise Architecture Improvement)

Deploy an internal Docker registry mirror:

- Nexus / Artifactory / Harbor
- Allow mirror to access upstream Docker Hub without TLS inspection
- Developers pull from internal mirror

Benefits:
- Eliminates TLS interception conflicts
- Improves reliability
- Avoids Docker Hub rate limits
- Improves auditability in regulated environments

---

## 8. Executive Summary

Docker image pull failures were caused by corporate TLS inspection (CN=Groww-Decryption-ECDSA) intercepting and modifying streamed image layer payloads, resulting in content hash mismatch and pull failure.

Resolution requires bypassing TLS inspection for Docker registry domains or deploying an internal registry mirror.

---

## 9. Status

Issue isolated and root cause identified.
Awaiting network policy adjustment.