---
description: Все настройки в папке config (копия config_sample).
---

# Настройка

### 1. Основные конфиги

1. В **config/**_**.env**_ **обязательно заполняем API ключи к основному и сабакам Okex .** Также не забудьте **добавить ваши кошели в Whitelist .** &#x20;
2. **config/wallets.csv -**  вставляем ваши приватники  + есть колонки bitget\_address и okx\_address где okx\_address обязательно для заполнения если будете ганять Orbiter или bitget\_address  если ганять USDV\
   _<mark style="color:red;">1 кошель = 1 отдельный адрес на бирже при депозите.</mark>_
3. **config/settings.py -** можно настроить рпс, слипы, MIN\_BALANCE в нативке каждой сети которые всегда оставлять на кошеле бриджах или свапах (можно диапазоном **'0.008-0.01'** )
4. Так же есть колонки **contract\_address**  и **contract\_type.** Если вы деплоили в скрол контракты мои скриптом [https://github.com/darcksday/deploy-contracts](https://github.com/darcksday/deploy-contracts) а конкретно  DepositContract StakingContract -   то у вас будет возможность взаемодейсвовать с етими контрактами и набивать обьем.

**Настоятельно рекомендую использывать** [**https://www.moderncsv.com/**](https://www.moderncsv.com/)  **для роботы с csv** **(он бесплатный и очень удобный) **<mark style="color:red;">**С другим csv софтом коректную роботу**</mark> <mark style="color:red;">**гарантировать не могу!**</mark>



<figure><img src=".gitbook/assets/Screenshot 2023-09-07 132534.png" alt=""><figcaption></figcaption></figure>

###







