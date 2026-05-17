-- Триггер 1. Автоматическое создание выписки при транзакции
CREATE TRIGGER IF NOT EXISTS update_account_statement
AFTER INSERT ON account_transaction
FOR EACH ROW
BEGIN
    -- Получаем текущий баланс счёта
    WITH current_balance AS (
        SELECT balance
        FROM account
        WHERE account_id = NEW.account_id
    )
    -- Вставляем запись в выписку
    INSERT INTO account_statement (
        account_id,
        transaction_id,
        operation_type,
        amount,
        balance_after,
        description
    )
    SELECT
        NEW.account_id,
        NEW.transaction_id,
        NEW.transaction_type,
        NEW.amount,
        CASE
            WHEN NEW.transaction_type IN ('deposit', 'transfer_in')
            THEN current_balance.balance + NEW.amount
            ELSE current_balance.balance - NEW.amount
        END,
        NEW.description
    FROM current_balance;

    -- Обновляем баланс счёта
    UPDATE account
    SET balance = (
        CASE
            WHEN NEW.transaction_type IN ('deposit', 'transfer_in')
            THEN balance + NEW.amount
            ELSE balance - NEW.amount
        END
    )
    WHERE account_id = NEW.account_id;
END;

-- Триггер 2. Автоматическое создание графика платежей при добавлении кредита
CREATE TRIGGER IF NOT EXISTS create_loan_schedule
AFTER INSERT ON loan
FOR EACH ROW
BEGIN
    WITH RECURSIVE months(n, date) AS (
        -- Первый платёж через месяц после начала кредита
        SELECT 1, DATE(NEW.start_date, '+1 month')
        UNION ALL
        SELECT n+1, DATE(date, '+1 month') FROM months
        WHERE date < NEW.end_date
    )
    INSERT INTO payment_schedule (
        loan_id,
        payment_date,
        amount,
        status
    )
    SELECT
        NEW.loan_id,
        date,
        ROUND(NEW.amount / (
            (julianday(NEW.end_date) - julianday(NEW.start_date)) / 30
        ), 2),
        'pending'
    FROM months;
END;

-- Триггер 3. Автоматическое начисление процентов по депозитам
CREATE TRIGGER IF NOT EXISTS calculate_deposit_interest
AFTER UPDATE ON deposit
FOR EACH ROW
WHEN NEW.status = 'active' AND OLD.status != 'active'
BEGIN
    INSERT INTO interest_calculation (
        deposit_id,
        calculation_date,
        interest_amount,
        applied_to_account
    )
    VALUES (
        NEW.deposit_id,
        DATE('now'),
        ROUND(
            NEW.amount * NEW.interest_rate / 100 / 12,
            2
        ),
        (
            SELECT account_id
            FROM account
            WHERE client_id = NEW.client_id
            LIMIT 1
        )
    );
END;

-- Триггер 4. Контроль просроченных платежей
CREATE TRIGGER IF NOT EXISTS check_overdue_payments
AFTER UPDATE OF status ON payment_schedule
FOR EACH ROW
WHEN NEW.status = 'pending' AND DATE(NEW.payment_date) < DATE('now')
BEGIN
    UPDATE payment_schedule
    SET status = 'overdue'
    WHERE schedule_id = NEW.schedule_id;
END;

-- Триггер 5. Автоматическое обновление статуса кредита при погашении
CREATE TRIGGER IF NOT EXISTS update_loan_status
AFTER UPDATE ON payment_schedule
FOR EACH ROW
WHEN NEW.status = 'paid'
BEGIN
    -- Проверяем, все ли платежи по кредиту оплачены
    UPDATE loan
    SET status = CASE
        WHEN (
            SELECT COUNT(*)
            FROM payment_schedule
            WHERE loan_id = NEW.loan_id AND status != 'paid'
        ) = 0
        THEN 'paid'
        ELSE 'active'
    END
    WHERE loan_id = NEW.loan_id;
END;

-- Триггер 6. Автоматическое списание платежа по кредиту
CREATE TRIGGER IF NOT EXISTS process_loan_payment
AFTER UPDATE ON payment_schedule
FOR EACH ROW
WHEN NEW.status = 'paid' AND OLD.status = 'pending'
BEGIN
    -- Находим счёт клиента
    WITH client_account AS (
        SELECT a.account_id
        FROM account a
        JOIN loan l ON a.client_id = l.client_id
        WHERE l.loan_id = NEW.loan_id
        LIMIT 1
    )
    -- Создаём транзакцию списания
    INSERT INTO account_transaction (
        account_id,
        transaction_type,
        amount,
        description
    )
    SELECT
        ca.account_id,
        'withdrawal',
        NEW.amount,
        'Платёж по кредиту №' || NEW.loan_id
    FROM client_account ca;

    -- Обновляем оставшийся долг по кредиту
    UPDATE loan
    SET remaining_amount = remaining_amount - NEW.amount
    WHERE loan_id = NEW.loan_id;
END;

-- Триггер 7. Автоматическое зачисление процентов на счёт
CREATE TRIGGER IF NOT EXISTS apply_interest_to_account
AFTER INSERT ON interest_calculation
FOR EACH ROW
BEGIN
    -- Зачисляем проценты на счёт
    INSERT INTO account_transaction (
        account_id,
        transaction_type,
        amount,
        description
    )
    VALUES (
        NEW.applied_to_account,
        'deposit',
        NEW.interest_amount,
        'Начисление процентов по депозиту №' || NEW.deposit_id
    );

    -- Обновляем статус расчёта процентов
    UPDATE interest_calculation
    SET applied_to_account = NEW.applied_to_account
    WHERE calculation_id = NEW.calculation_id;
END;

-- Триггер 8. Контроль минимального баланса счёта
CREATE TRIGGER IF NOT EXISTS check_minimum_balance
BEFORE INSERT ON account_transaction
FOR EACH ROW
WHEN NEW.transaction_type = 'withdrawal'
BEGIN
    -- Проверяем, достаточно ли средств на счёте
    SELECT CASE
        WHEN (SELECT balance FROM account WHERE account_id = NEW.account_id) < NEW.amount
        THEN RAISE(ABORT, 'Недостаточно средств на счёте для выполнения операции')
    END;
END;
