# Стандарты безопасности SJK SmartView

Этот документ описывает обязательные требования к безопасности при разработке и эксплуатации системы.

## 1. Управление секретами (Secret Management)

### Правило «Нулевой терпимости» к хардкоду
Запрещено указывать любые API-ключи, токены или пароли в исходном коде.
- **Frontend**: Все ключи должны иметь префикс `NEXT_PUBLIC_` и храниться в `.env`. В коде используется только `process.env.NEXT_PUBLIC_...`.
- **Backend**: Все секреты (Modal Token, Firebase Admin) хранятся в `.env` и пробрасываются через переменные окружения.

### Изоляция Service Account
Файл ключа Firebase Admin SDK (`service_account.json`):
1. **ВСЕГДА** должен быть в `.gitignore`.
2. На сервере/локально должен иметь права доступа `600` (`chmod 600 service_account.json`).
3. Никогда не должен передаваться через открытые каналы связи (Slack, Email в открытом виде).

## 2. Облачная инфраструктура

### Firebase Storage Rules
Доступ к хранилищу ограничен следующими правилами:
- **Read**: Публичный доступ (для отображения в КП и приложении).
- **Write**: Только для аутентифицированных пользователей с ролью `manager`.

```javascript
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

### Modal.com Security
- Доступ осуществляется через `MODAL_TOKEN_ID` и `MODAL_TOKEN_SECRET`.
- При компрометации токена — немедленная ротация в панели управления Modal.

## 3. Процедура ротации ключей

При подозрении на утечку (например, случайный коммит в Git):
1. **Firebase API Key**: Google Cloud Console -> APIs & Services -> Credentials -> Create New Key / Delete Old Key.
2. **Firebase Admin**: Firebase Settings -> Service Accounts -> Generate New Private Key. Удалить старый ключ в IAM.
3. **Modal**: Settings -> API Tokens -> Revoke old, Create new.
4. Обновить значения в локальном `.env` и выполнить `docker compose restart`.

---
*Документ актуализирован: 13.04.2026*
