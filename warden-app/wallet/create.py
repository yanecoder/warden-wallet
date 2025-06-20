from mnemonic import Mnemonic
from ecdsa import SigningKey, SECP256k1

def generate_mnemonic() -> str:
    mnemo = Mnemonic()
    phrase = mnemo.generate(strength=256)
    return phrase

from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

def get_address(mnemonic: str) -> str:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.RIPPLE)
    account = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

    return account.PublicKey().ToAddress()

def is_valid_mnemonic(mnemo: str) -> bool:
    return Mnemonic("english").check(mnemo)


def mnemonic_to_private_key(mnemonic: str) -> str:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.RIPPLE)
    private_key = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PrivateKey().Raw().ToHex()
    return private_key

def hex_priv_to_public_key(raw: str) -> str:

    sk = SigningKey.from_string(bytes.fromhex(raw), curve=SECP256k1)
    vk = sk.verifying_key
    x = vk.to_string()[:32]
    y = vk.to_string()[32:]
    prefix = b"\x02" if (y[-1] % 2 == 0) else b"\x03"
    public_key_hex = (prefix + x).hex().upper()

    return public_key_hex