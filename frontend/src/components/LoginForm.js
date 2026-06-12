import React, { useState } from 'react';
import { authAPI } from '../services/api';  // импортируем ваш API

function LoginForm({ onLoginSuccess, onSwitchToRegister }) {
  const [username, setUsername] = useState(''); //для хранения того, что ввел пользователь
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  //при нажатии кнопки вход не перезагружаем страницу и очищаем ошибку
  const handleSubmit = async (e) => {e.preventDefault();setError('');

    try {
      //ответ от сервера
      const response = await authAPI.login(username, password);
      const data = response.data;

      //сохраняем данные на компьютере
      localStorage.setItem('api_key', data.api_key);
      localStorage.setItem('user', JSON.stringify({
        username: data.username,
        role: data.role,
        user_id: data.user_id,
      }));

      //переход в приложение
      onLoginSuccess(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа, проверьте логин или пароль');
    }
  };



  //разметка страницы
  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2 style={styles.title}>Вход в систему</h2>
        
        {error && <div style={styles.error}>{error}</div>}
        
        <input
          type="text"
          placeholder="Имя пользователя"
          style={styles.input}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        
        <input
          type="password"
          placeholder="Пароль"
          style={styles.input}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        <button type="submit" style={styles.button}>
          Войти
        </button>
        
        <p style={styles.link}>
          Нет аккаунта?{' '}
          <span onClick={onSwitchToRegister} style={styles.linkSpan}>
            Зарегистрироваться
          </span>
        </p>
      </form>
    </div>
  );
}



//стили
//фон
const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: '#87CEEB',
  },

  //карточка входа
  form: {
    background: 'white',
    padding: '50px',
    borderRadius: '16px',
    width: '100%',
    maxWidth: '400px',
  },

  //заголовок
  title: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#000000',
  },

  //поля ввода
  input: {
    width: '100%',
    padding: '12px',
    marginBottom: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    boxSizing: 'border-box',
  },

  //кнопка войти
  button: {
    width: '100%',
    padding: '12px',
    background: '#87CEEB',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '10px',
  },

  //блок с ошибкой
  error: {
    background: '#fee',
    color: '#6c757d',
    padding: '10px',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center',
  },

  //текст нет аккаунта
  link: {
    textAlign: 'center',
    marginTop: '20px',
    color: '#000000',
  },

  //ссылка зарегистрироваться
  linkSpan: {
    color: '#87CEEB',
    cursor: 'pointer',
    textDecoration: 'underline',
  },
};

export default LoginForm;