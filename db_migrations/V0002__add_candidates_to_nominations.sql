CREATE TABLE IF NOT EXISTS candidates (
  id SERIAL PRIMARY KEY,
  nomination_id INTEGER REFERENCES nominations(id),
  name VARCHAR(255) NOT NULL,
  votes INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_votes DROP CONSTRAINT IF EXISTS user_votes_nomination_id_user_ip_key;
ALTER TABLE user_votes ADD COLUMN IF NOT EXISTS candidate_id INTEGER REFERENCES candidates(id);

INSERT INTO candidates (nomination_id, name, votes) VALUES
  (1, 'Александр Иванов', 0),
  (1, 'Мария Петрова', 0),
  (1, 'Дмитрий Сидоров', 0),
  (2, 'Анна Козлова', 0),
  (2, 'Игорь Морозов', 0),
  (2, 'Елена Васильева', 0),
  (3, 'Сергей Новиков', 0),
  (3, 'Ольга Федорова', 0),
  (3, 'Максим Волков', 0),
  (4, 'Наталья Соколова', 0),
  (4, 'Андрей Лебедев', 0),
  (4, 'Татьяна Егорова', 0),
  (5, 'Владимир Павлов', 0),
  (5, 'Ирина Семенова', 0),
  (5, 'Алексей Кузнецов', 0),
  (6, 'Юлия Михайлова', 0),
  (6, 'Денис Алексеев', 0),
  (6, 'Светлана Николаева', 0),
  (7, 'Роман Григорьев', 0),
  (7, 'Екатерина Данилова', 0),
  (7, 'Павел Захаров', 0),
  (8, 'Виктория Романова', 0),
  (8, 'Константин Борисов', 0),
  (8, 'Людмила Андреева', 0),
  (9, 'Валерий Степанов', 0),
  (9, 'Оксана Макарова', 0),
  (9, 'Артем Матвеев', 0),
  (10, 'Дарья Тимофеева', 0),
  (10, 'Николай Белов', 0),
  (10, 'Вероника Зайцева', 0);

CREATE UNIQUE INDEX IF NOT EXISTS user_votes_candidate_ip ON user_votes(candidate_id, user_ip) WHERE candidate_id IS NOT NULL;
