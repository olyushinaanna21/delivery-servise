import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import UserPage from './components/UserPage';
import AdminPage from './components/AdminPage';
import CourierPage from './components/CourierPage';


function App() {
  const [isLogin, setIsLogin] = useState(true); //форма входа
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem('api_key') //залогинен или нет
  );


  //успешный вход
  const handleAuthSuccess = (userData) => {
    setIsAuthenticated(true);
    console.log('Добро пожаловать,', userData.username);
  };


  //выход
  const handleLogout = () => {
    localStorage.removeItem('api_key');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
  };


  //если не авторизован показываем регистрацию, если авторизован вход
  if (!isAuthenticated) {
    return isLogin ? (
      <LoginForm
        onLoginSuccess={handleAuthSuccess}
        onSwitchToRegister={() => setIsLogin(false)}
      />
    ) : (
      <RegisterForm
        onRegisterSuccess={handleAuthSuccess}
        onSwitchToLogin={() => setIsLogin(true)}
      />
    );
  }




//после входа определяем роль по его апи ключу и показываем нужную страницу
const user = JSON.parse(localStorage.getItem('user') || '{}');

if (user.role === 'admin') {
  return <AdminPage onLogout={handleLogout} />;
}

if (user.role === 'courier') {
  return <CourierPage onLogout={handleLogout} />;
}

return <UserPage onLogout={handleLogout} />;
}

export default App;


