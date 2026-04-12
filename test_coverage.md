# Примеры IT вакансий и тестовое покрытие

## 1️⃣ Junior Python Developer

### Вакансия:
- **Стек:** Python, Django/FastAPI, PostgreSQL
- **Требуемые навыки:** ООП, работа с БД, REST API
- **Готовность обучать:** Да
- **Опыт:** 0-1 год (но не требуется строго)

### Тестовое покрытие:

#### Quiz (10 минут):
```
1. Что такое виртуальное окружение в Python?
   a) Изолированная среда для проекта
   b) Окружение в облаке
   c) Отладчик кода
   Ответ: a

2. Какой паттерн используется для создания объектов?
   a) Factory
   b) Singleton
   c) Iterator
   Ответ: a/b

3. JOIN в SQL нужен для...
   a) Объединения таблиц по условию
   b) Изменения записей
   c) Удаления данных
   Ответ: a
```

#### Code Challenge (30 минут):
```python
# Задача: Напиши функцию для работы с БД пользователей

def get_users_by_role(db_connection, role: str) -> list:
    """
    Получить всех пользователей с определённой ролью.
    
    Args:
        db_connection: подключение к БД
        role: роль пользователя (admin, user, moderator)
    
    Returns:
        Список пользователей или []
    """
    # TODO: Реализуй функцию
    pass


# Тесты для проверки:
def test_get_users_by_role_admin():
    # Должна вернуть только админов
    users = get_users_by_role(mock_db, "admin")
    assert len(users) == 2
    assert all(u["role"] == "admin" for u in users)

def test_get_users_by_role_invalid():
    # Несуществующая роль возвращает пусто
    users = get_users_by_role(mock_db, "superuser")
    assert users == []

def test_get_users_by_role_empty():
    # Если нет юзеров, вернуть []
    users = get_users_by_role(empty_db, "user")
    assert users == []
```

---

## 2️⃣ Junior Frontend Developer (React)

### Вакансия:
- **Стек:** React, TypeScript, Tailwind CSS
- **Требуемые навыки:** JavaScript, компоненты, управление состоянием (useState/useContext)
- **Готовность обучать:** Да
- **Опыт:** 0-6 месяцев

### Тестовое покрытие:

#### Quiz (10 минут):
```
1. Что такое JSX?
   a) Синтаксис для описания UI
   b) Язык программирования
   c) Фреймворк
   Ответ: a

2. Какой хук используется для управления состоянием?
   a) useEffect
   b) useState
   c) useContext
   Ответ: b

3. Что вернёт Array.map() для пустого массива?
   a) null
   b) undefined
   c) пустой массив []
   Ответ: c
```

#### Code Challenge (30 минут):
```jsx
// Задача: Реализуй компонент счётчика с кнопками +1, -1, Reset

export function Counter() {
  // TODO: Добавь state и функции
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Count: {/* Значение счётчика */}</h1>
      <button onClick={/* функция +1 */}>Increment</button>
      <button onClick={/* функция -1 */}>Decrement</button>
      <button onClick={/* Reset */}>Reset</button>
    </div>
  );
}

// Тест:
test("Counter increments when button clicked", () => {
  render(<Counter />);
  const btn = screen.getByText("Increment");
  fireEvent.click(btn);
  expect(screen.getByText("Count: 1")).toBeInTheDocument();
});
```

---

## 3️⃣ Junior Java Developer

### Вакансия:
- **Стек:** Java, Spring Boot, MySQL
- **Требуемые навыки:** ООП, Collections, SQL
- **Готовность обучать:** Да
- **Опыт:** 0-1 год

### Тестовое покрытие:

#### Quiz (10 минут):
```
1. Что такое интерфейс в Java?
   a) Договор для класса
   b) Класс абстрактный
   c) Переменная
   Ответ: a

2. Разница между ArrayList и LinkedList?
   a) ArrayList быстрее по доступу, LinkedList по вставке
   b) Они идентичны
   c) LinkedList быстрее всегда
   Ответ: a

3. Для чего нужна аннотация @Override?
   a) Переопределить метод родителя
   b) Компилятор проверит корректность
   c) a и b
   Ответ: c
```

#### Code Challenge (30 минут):
```java
// Задача: Напиши класс User с валидацией

public class User {
    private String name;
    private String email;
    private int age;
    
    // TODO: конструктор, getters/setters, валидация
    
    public void validate() throws IllegalArgumentException {
        // Проверить: name не пусто, email содержит @, age > 0
    }
}

// Тест:
@Test
public void testUserValidationFails() {
    User user = new User("", "invalid-email", -5);
    assertThrows(IllegalArgumentException.class, user::validate);
}

@Test
public void testUserValidationSuccess() {
    User user = new User("John", "john@example.com", 25);
    assertDoesNotThrow(user::validate);
}
```

---

## 4️⃣ Junior DevOps / Backend (Node.js)

### Вакансия:
- **Стек:** Node.js, Express, MongoDB/PostgreSQL
- **Требуемые навыки:** API, асинхронность, работа с сервером
- **Готовность обучать:** Да
- **Опыт:** 0-6 месяцев

### Тестовое покрытие:

#### Quiz (10 минут):
```
1. Что такое Promise?
   a) Объект асинхронной операции
   b) Обещание значение в будущем
   c) a и b
   Ответ: c

2. Какой статус HTTP означает успех?
   a) 200 OK
   b) 404 Not Found
   c) 500 Server Error
   Ответ: a

3. Что делает async/await?
   a) Упрощает работу с Promise
   b) Ускоряет код
   c) Заменяет callbacks
   Ответ: a
```

#### Code Challenge (30 минут):
```javascript
// Задача: Напиши Express middleware для проверки авторизации

async function getUser(userId) {
  // Получить пользователя из БД (имитируем)
  // Вернуть объект {id, name, role}
}

function authMiddleware(req, res, next) {
  // TODO: проверить есть ли токен
  // если нет - вернуть 401
  // если есть - добавить user в req и вызвать next()
}

// Тест:
test("authMiddleware should return 401 if no token", (done) => {
  const req = { headers: {} };
  const res = { status: jest.fn().mockReturnThis(), json: jest.fn() };
  
  authMiddleware(req, res, () => {});
  
  expect(res.status).toHaveBeenCalledWith(401);
  done();
});
```

---

## 5️⃣ Junior QA / Test Automation

### Вакансия:
- **Стек:** Selenium/Cypress, JavaScript, HTTP
- **Требуемые навыки:** Тестирование, логика, основы программирования
- **Готовность обучать:** Да
- **Опыт:** 0-6 месяцев

### Тестовое покрытие:

#### Quiz (10 минут):
```
1. Что такое unit-тест?
   a) Тест одной функции/метода
   b) Тест всей системы
   c) Тест интеграции
   Ответ: a

2. Что проверяет assertion?
   a) Условие истинно/ложно
   b) Нет ошибок в коде
   c) Производительность
   Ответ: a

3. Какой тип тестов проверяет взаимодействие компонентов?
   a) Unit-тесты
   b) Integration тесты
   c) E2E тесты
   Ответ: b/c
```

#### Code Challenge (30 минут):
```javascript
// Задача: Напиши тесты для простой функции калькулятора

function add(a, b) { return a + b; }
function multiply(a, b) { return a * b; }
function divide(a, b) { if (b === 0) throw Error("Division by zero"); return a / b; }

// TODO: Напиши тесты используя Jest или Mocha
// Проверь:
// - add(2, 3) === 5
// - multiply(4, 5) === 20
// - divide(10, 2) === 5
// - divide(10, 0) выбросит ошибку

describe("Calculator", () => {
  test("add works correctly", () => {
    expect(add(2, 3)).toBe(5);
  });
  
  // TODO: добавь остальные тесты
});
```

---

## 📊 Резюме:

| Должность | Сложность квиза | Сложность кода | Время на тест | Итого |
|-----------|-----------------|----------------|---------------|-------|
| Python Dev | Средняя | Средняя | 40 мин | Junior |
| Frontend | Средняя | Простая | 40 мин | Junior |
| Java Dev | Средняя | Средняя | 40 мин | Junior |
| Node.js | Средняя | Средняя | 40 мин | Junior |
| QA | Простая | Простая | 40 мин | Junior/Entry |

---

## 💡 Как это убедит HR:

✅ **"Смотрите, этот парень прошёл наш тест за 35 минут на 85/100"** — это объективная метрика  
✅ **Реальные навыки** — не степень и не опыт  
✅ **Справедливость** — все проходят одни тесты  
✅ **Риск минимален** — вы видите способность решать задачи  

