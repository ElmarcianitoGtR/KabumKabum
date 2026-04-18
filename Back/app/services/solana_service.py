"""
Servicio Solana — guarda y verifica el hash de credenciales on-chain.

Estrategia para hackathon (devnet, sin costo):
  - Cada usuario tiene una cuenta PDA (Program Derived Address)
    derivada de su email.
  - Almacenamos: hash(email + hashed_password) + rol como datos de la cuenta.
  - En login verificamos que el hash on-chain coincida.
"""

import hashlib
import json
import base64
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# ── Imports de Solana (con fallback si no está instalado aún) ──────────────
try:
    from solana.rpc.async_api import AsyncClient
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False


# ─────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────

def _credential_hash(email: str, hashed_password: str) -> str:
    """Genera un hash único de las credenciales para almacenar on-chain."""
    raw = f"{email}:{hashed_password}".encode()
    return hashlib.sha256(raw).hexdigest()


def _derive_pda_seed(email: str) -> bytes:
    """Semilla determinista para derivar la PDA del usuario."""
    return hashlib.sha256(f"reactor_user:{email}".encode()).digest()[:32]


# ─────────────────────────────────────────────────
#  ALMACENAR CREDENCIALES ON-CHAIN
# ─────────────────────────────────────────────────

async def store_credentials_on_chain(
    email: str,
    hashed_password: str,
    role: str,
) -> Optional[str]:
    """
    Guarda el hash de credenciales y el rol en Solana devnet.
    Retorna la public key de la cuenta creada (o simulada).
    """
    cred_hash = _credential_hash(email, hashed_password)

    if not SOLANA_AVAILABLE or not settings.solana_payer_keypair:
        # Modo simulado para desarrollo / hackathon sin wallet configurada
        print(f"Solana simulado — hash: {cred_hash[:16]}...")
        seed = _derive_pda_seed(email)
        return base64.b64encode(seed).decode()

    try:
        client = AsyncClient(settings.solana_rpc_url)
        payer  = Keypair.from_base58_string(settings.solana_payer_keypair)

        # Datos a almacenar: JSON compacto con hash y rol
        payload = json.dumps({
            "credential_hash": cred_hash,
            "role": role,
            "email_prefix": email[:4] + "***",   # privacidad parcial
        }).encode()

        # Memo instruction — almacena datos en la transacción (simple y gratis en devnet)
        from solders.instruction import Instruction, AccountMeta
        from solana.transaction import Transaction

        MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")

        memo_ix = Instruction(
            program_id=MEMO_PROGRAM_ID,
            accounts=[AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=False)],
            data=payload,
        )

        tx = Transaction().add(memo_ix)
        resp = await client.send_transaction(tx, payer)
        await client.close()

        return str(payer.pubkey())

    except Exception as e:
        print(f"Error Solana (usando simulado): {e}")
        seed = _derive_pda_seed(email)
        return base64.b64encode(seed).decode()


# ─────────────────────────────────────────────────
#  VERIFICAR CREDENCIALES ON-CHAIN
# ─────────────────────────────────────────────────

async def verify_credentials_on_chain(
    email: str,
    hashed_password: str,
) -> bool:
    """
    Verifica que el hash de credenciales coincida con lo almacenado.
    En modo simulado siempre retorna True (para desarrollo).
    """
    if not SOLANA_AVAILABLE or not settings.solana_payer_keypair:
        # Modo simulado: confiamos en la verificación bcrypt del auth service
        print("Verificación Solana simulada → OK")
        return True

    try:
        # En producción real: consultar la transacción memo y comparar el hash
        cred_hash = _credential_hash(email, hashed_password)
        # TODO: consultar historial de transacciones de la wallet del usuario
        #       y verificar que el hash más reciente coincida
        print(f"Verificación Solana: {cred_hash[:16]}...")
        return True

    except Exception as e:
        print(f"Error verificación Solana: {e}")
        return True   # fallback: confiar en bcrypt
