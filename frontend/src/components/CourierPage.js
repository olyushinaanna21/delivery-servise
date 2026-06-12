import React, { useState, useEffect } from 'react';
import { courierAPI } from '../services/api';

function CourierPage({ onLogout }) {
  const [activeTab, setActiveTab] = useState('available');
  const [profile, setProfile] = useState(null);
  const [availableOrders, setAvailableOrders] = useState([]);
  const [myOrders, setMyOrders] = useState([]);
  const [earnings, setEarnings] = useState(0);
  const [rating, setRating] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
    fetchAvailableOrders();
    fetchMyOrders();
    fetchEarnings();
    fetchRating();
  }, []);


  //получение профиля
  const fetchProfile = async () => {
    try {
      const response = await courierAPI.getProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Ошибка загрузки профиля');
    }
  };


  //получение доступных заказов
  const fetchAvailableOrders = async () => {
    try {
      const response = await courierAPI.getAvailableOrders();
      setAvailableOrders(response.data.orders || []);
    } catch (error) {
      console.error('Ошибка загрузки доступных заказов');
    }
  };


  //получение своих взятых заказов
  const fetchMyOrders = async () => {
    try {
      const response = await courierAPI.getMyOrders();
      setMyOrders(response.data.orders || []);
    } catch (error) {
      console.error('Ошибка загрузки моих заказов');
    }
  };


  //получение рейтинга и заработка
  const fetchEarnings = async () => {
    try {
      const response = await courierAPI.getEarnings();
      setEarnings(response.data.earnings);
    } catch (error) {
      console.error('Ошибка загрузки заработка');
    }
  };

  const fetchRating = async () => {
    try {
      const response = await courierAPI.getRating();
      setRating(response.data.rating);
    } catch (error) {
      console.error('Ошибка загрузки рейтинга');
    }
  };



  const takeOrder = async (orderId) => {
    setLoading(true);
    try {
      await courierAPI.takeOrder(orderId);
      setMessage(`Заказ ${orderId} взят!`);
      fetchAvailableOrders();
      fetchMyOrders();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Ошибка: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
      setTimeout(() => setMessage(''), 3000);
    }
    setLoading(false);
  };

  const completeOrder = async (orderId) => {
    if (!window.confirm('Выполнить заказ?')) return;
    setLoading(true);
    try {
      await courierAPI.completeOrder(orderId);
      setMessage(`Заказ ${orderId} выполнен`);
      fetchMyOrders();
      fetchEarnings();
      fetchRating();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Ошибка выполнения заказа ');
      setTimeout(() => setMessage(''), 3000);
    }
    setLoading(false);
  };



  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Курьерская панель</h1>
        <button onClick={onLogout} style={styles.logoutButton}>Выйти</button>
      </div>

      {message && <div style={styles.message}>{message}</div>}

      {/*профиль */}
      {profile && (
        <div style={styles.profile}>
          <h3>Мой профиль</h3>
          <div style={styles.profileInfo}>
            <span><strong>Тип:</strong> {profile.courier_type === 'foot' ? 'Пеший' : profile.courier_type === 'bike' ? 'Велосипед' : 'Автомобиль'}</span>
            <span><strong>Регионы:</strong> {profile.regions?.join(', ')}</span>
            <span><strong>Часы работы:</strong> {profile.working_hours?.join(', ')}</span>
            <span><strong>Грузоподъёмность:</strong> {profile.max_load} кг</span>
            <span><strong>Заработок:</strong> {earnings} ₽</span>
            <span><strong>Рейтинг:</strong> {rating === 0 ? 'Нет оценок' : rating.toFixed(2)}</span>
          </div>
        </div>
      )}

      {/*вкладки */}
      <div style={styles.tabs}>
        <button onClick={() => setActiveTab('available')} style={{...styles.tab, ...(activeTab === 'available' ? styles.activeTab : {})}}>Доступные заказы</button>
        <button onClick={() => setActiveTab('my')} style={{...styles.tab, ...(activeTab === 'my' ? styles.activeTab : {})}}>Мои заказы</button>
        <button onClick={() => setActiveTab('stats')} style={{...styles.tab, ...(activeTab === 'stats' ? styles.activeTab : {})}}>Статистика</button>
      </div>

      {/*доступные заказы */}
      {activeTab === 'available' && (
        <div style={styles.section}>
          <h2>Доступные заказы</h2>
          {availableOrders.length === 0 ? (
            <p>Нет доступных заказов</p>
          ) : (
            <div style={styles.ordersList}>
              {availableOrders.map(order => (
                <div key={order.order_id} style={styles.orderCard}>
                  <h3>Заказ #{order.order_id}</h3>
                  <p><strong>Вес:</strong> {order.weight} кг</p>
                  <p><strong>Регион:</strong> {order.region}</p>
                  <p><strong>Время доставки:</strong> {order.delivery_hours?.join(', ')}</p>
                  <button onClick={() => takeOrder(order.order_id)} disabled={loading} style={styles.takeButton}>Взять заказ</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/*мои заказы */}
      {activeTab === 'my' && (
        <div style={styles.section}>
          <h2>Мои заказы</h2>
          {myOrders.length === 0 ? (
            <p>Нет активных заказов</p>
          ) : (
            <div style={styles.ordersList}>
              {myOrders.map(order => (
                <div key={order.order_id} style={styles.orderCard}>
                  <h3>Заказ #{order.order_id}</h3>
                  <p><strong>Вес:</strong> {order.weight} кг</p>
                  <p><strong>Регион:</strong> {order.region}</p>
                  <p><strong>Время доставки:</strong> {order.delivery_hours?.join(', ')}</p>
                  <p><strong>Взято в работу:</strong> {order.assign_time ? new Date(order.assign_time).toLocaleString() : 'Не указано'}</p>
                  <button onClick={() => completeOrder(order.order_id)} disabled={loading} style={styles.completeButton}>Выполнить</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/*статистика */}
      {activeTab === 'stats' && (
        <div style={styles.section}>
          <h2>Моя статистика</h2>
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <h3>Заработок</h3>
              <p style={styles.statValue}>{earnings} ₽</p>
            </div>
            <div style={styles.statCard}>
              <h3>Рейтинг</h3>
              <p style={styles.statValue}>{rating === 0 ? 'Нет оценок' : rating.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  title: { margin: 0 },
  logoutButton: { backgroundColor: '#6c757d', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  message: { padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', marginBottom: '20px' },
  profile: { backgroundColor: '#e3f2fd', padding: '20px', borderRadius: '8px', marginBottom: '20px' },
  profileInfo: { display: 'flex', flexWrap: 'wrap', gap: '20px', marginTop: '10px' },
  tabs: { display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' },
  tab: { padding: '10px 20px', backgroundColor: '#f0f0f0', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
  activeTab: { backgroundColor: '#007bff', color: 'white' },
  section: { backgroundColor: '#f9f9f9', padding: '20px', borderRadius: '8px' },
  ordersList: { display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' },
  orderCard: { backgroundColor: 'white', padding: '15px', borderRadius: '8px', border: '1px solid #ddd' },
  takeButton: { backgroundColor: '#bbdef5', color: 'white', padding: '8px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' },
  completeButton: { backgroundColor: '#6c757d', color: 'black', padding: '8px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px', marginTop: '15px' },
  statCard: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  statValue: { fontSize: '28px', fontWeight: 'bold', color: '#007bff', margin: '10px 0' }
};

export default CourierPage;