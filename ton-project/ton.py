from pytoniq_core import Address, begin_cell
from tonutils.client import ToncenterV3Client
from tonutils.jetton import JettonMasterStandard, JettonWalletStandard
from tonutils.wallet import WalletV4R2

from datetime import datetime

import os


async def validate_address(address: str) -> bool:
    try:
        addr = Address(address)
        return True

    except Exception:
        return False


async def transfer_jetton(recipient: str, amount: int):
    print(f'Новый перевод: {recipient}, {amount}')

    mnemonic = os.getenv('MNEMONIC')
    jetton_master_address = os.getenv('JETTON_MASTER_ADDRESS')
    comment = "Токенизация умникоинов и талантов"
    decimals = 9
    gas_amount = 0.05

    # 1. Инициализируем клиент для взаимодействия с блокчейном
    client = ToncenterV3Client(is_testnet=False, rps=1, max_retries=1)

    # 2. Восстанавливаем кошелёк отправителя из мнемоники
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, mnemonic)

    # 3. Получаем адрес jetton-кошелька отправителя
    jetton_wallet_address = await JettonMasterStandard.get_wallet_address(
        client=client,
        owner_address=wallet.address.to_str(),
        jetton_master_address=jetton_master_address,
    )

    # 4. Подготавливаем полезную нагрузку (payload) для комментария, если он есть
    forward_payload = None
    if comment:
        forward_payload = (
            begin_cell()
            .store_uint(0, 32)  # Opcode для текстового комментария
            .store_snake_string(comment)  # Сам комментарий
            .end_cell()
        )

    # 5. Создаём тело транзакции перевода jettons
    body = JettonWalletStandard.build_transfer_body(
        recipient_address=Address(recipient),
        response_address=wallet.address,
        jetton_amount=int(amount * (10 ** decimals)),  # Пересчёт в базовые единицы (нано)
        forward_payload=forward_payload,
        forward_amount=1,  # Минимальное количество наноTON для форварда уведомления
    )

    # 6. Отправляем транзакцию, которая инициирует перевод с jetton-кошелька
    tx_hash = await wallet.transfer(
        destination=jetton_wallet_address,  # Адрес jetton-кошелька отправителя
        amount=gas_amount,  # TON на комиссию
        body=body,
    )

    if tx_hash:
        now = datetime.now()
        now = now.strftime('%Y/%m/%d %H:%M:%S')

        print(f"{now} ✅ Запрос на перевод {amount} MOZGI на кошелёк {recipient} отправлен в сеть. Хэш: {tx_hash}")
        return tx_hash

    else:
        print("❌ Ошибка при отправке транзакции.")
        return 'error'
