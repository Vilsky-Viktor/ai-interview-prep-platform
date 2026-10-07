import { createCipheriv, createHmac, randomBytes } from "node:crypto"

/** `text` sealed as a Fernet token with `key` (urlsafe base64, 32 bytes: signing then
 * encryption), as the companies service seals ATS keys, so it can read it back. */
export function fernetEncrypt(key: string, text: string): string {
  const raw = Buffer.from(key, "base64url")
  const iv = randomBytes(16)
  const cipher = createCipheriv("aes-128-cbc", raw.subarray(16), iv)
  const time = Buffer.alloc(8)
  time.writeBigUInt64BE(BigInt(Math.floor(Date.now() / 1000)))
  const body = Buffer.concat([
    Buffer.from([0x80]),
    time,
    iv,
    cipher.update(text, "utf8"),
    cipher.final(),
  ])
  const signature = createHmac("sha256", raw.subarray(0, 16)).update(body).digest()

  return Buffer.concat([body, signature]).toString("base64url").padEnd(
    Math.ceil((body.length + 32) / 3) * 4,
    "="
  )
}
