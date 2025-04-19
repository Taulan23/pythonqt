-- Добавление столбца gender в таблицу patients
ALTER TABLE patients ADD COLUMN gender VARCHAR(10) DEFAULT 'Мужской';

-- Обновление существующих записей
UPDATE patients SET gender = 'Мужской' WHERE id > 0; 