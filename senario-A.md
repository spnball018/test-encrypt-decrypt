## Scenario A: Key Rotation Strategy — Zero-Downtime DEK Migration

### Question
We need to rotate our Data Encryption Keys (DEK) annually for compliance. However, we have millions of encrypted records in the database.

Design a zero-downtime strategy to migrate these millions of records to the new key. How does the system know which key to use for decryption during the transition period?  
*(Hint: Key Versioning)*

---

### Answer

A zero-downtime key rotation strategy can be implemented using **key versioning + adapter-based encryption/decryption + background migration**.

---

## 🔐 Key Ideas

- Store **encryption version** with each encrypted value
- Use **version-based adapters** to decrypt correctly
- Introduce a **new adapter** for the rotated key
- Run **background migration** to re-encrypt existing data gradually
- Keep system readable/writable during the entire transition

---

## 1️⃣ Store Encryption Version with Each Record

The system already stores an encryption version together with the encrypted `national_id` field (or metadata column).

This version tells the system which key/adapter must be used to decrypt.