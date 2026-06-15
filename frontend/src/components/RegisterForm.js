import React, { useState } from 'react';
import { authAPI } from '../services/api';



function RegisterForm({ onRegisterSuccess, onSwitchToLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    address: '',
    region: '',
  });
  const [error, setError] = useState(''); //состояние ошибки


  //обработка изменения только тех полей, которые изменил пользователь
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };


  //отправка формы
  const handleSubmit = async (e) => {
    e.preventDefault(); //не перезагружем страницу и пустая ошибка
    setError('');


     const regionNum = parseInt(formData.region);
    if (formData.region && (regionNum < 1 || regionNum > 5)) {
      setError('Регион должен быть от 1 до 5');
      return;
    }


    try {
      const response = await authAPI.register(formData);
      const data = response.data;

      localStorage.setItem('api_key', data.api_key);
      localStorage.setItem('user', JSON.stringify({
        username: data.username,
        role: 'customer',
        user_id: data.user_id,
      }));

      onRegisterSuccess(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    }
  };

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <h2 style={styles.title}>Регистрация</h2>
        
        {error && <div style={styles.error}>{error}</div>}
        
        <input name="username" placeholder="Имя пользователя *" style={styles.input} value={formData.username} onChange={handleChange} required />
        <input name="email" type="email" placeholder="Email *" style={styles.input} value={formData.email} onChange={handleChange} required />
        <input name="password" type="password" placeholder="Пароль *" style={styles.input} value={formData.password} onChange={handleChange} required />
        <input name="address" placeholder="Адрес" style={styles.input} value={formData.address} onChange={handleChange} />
        <input name="region" placeholder="Регион" style={styles.input} value={formData.region} onChange={handleChange} />
        
        <button type="submit" style={styles.button}>Зарегистрироваться</button>
        
        <p style={styles.link}>Уже есть аккаунт? <span onClick={onSwitchToLogin} style={styles.linkSpan}>Войти</span></p>
      </form>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: '#87CEEB',
  },
  form: {
    background: 'white',
    padding: '40px',
    borderRadius: '16px',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#000000',
  },
  input: {
    width: '100%',
    padding: '12px',
    marginBottom: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    boxSizing: 'border-box',
  },
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
  error: {
    background: '#fee',
    color: '#6c757d',
    padding: '10px',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center',
  },
  link: {
    textAlign: 'center',
    marginTop: '20px',
    color: '#666',
  },
  linkSpan: {
    color: '#87CEEB',
    cursor: 'pointer',
    textDecoration: 'underline',
  },
};

export default RegisterForm;