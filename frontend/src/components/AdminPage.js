import React, { useState, useEffect } from 'react'; //хранение данных, загрузка страницы
import { adminAPI, productsAPI, couriersAPI } from '../services/api';


//выход из админа
function AdminPage({ onLogout }) {

  //состояние какая вкладка открыта
  const [activeTab, setActiveTab] = useState('products');

  //список товаров
  const [products, setProducts] = useState([]);

  //список пользователей
  const [users, setUsers] = useState([]);

  //список заказов
  const [orders, setOrders] = useState([]);

  //список курьеров
  const [couriers, setCouriers] = useState([]);

  //индикация загрузки
  const [loading, setLoading] = useState(false);

  //сообщение успеха или ошибки
  const [message, setMessage] = useState('');
  


  //форма нового товара
  const [newProduct, setNewProduct] = useState({
    id: '',
    name: '',
    description: '',
    price: '',
    weight: '',
    category: ''
  });
  

  //форма нового курьера
  const [newCourier, setNewCourier] = useState({
    username: '',
    email: '',
    password: '',
    courier_type: 'foot',
    regions: [1],
    working_hours: ['09:00-18:00']
  });


  //загрузка данных при открытии страницы
  useEffect(() => {
    fetchProducts();
    fetchUsers();
    fetchOrders();
    fetchCouriers();
  }, []);


  //загрузка товаров с бэка
  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getAll(); //гет запрос 
      setProducts(response.data.products || []); //сохраняем в состояние
    } catch (error) {
      console.error('Ошибка загрузки товаров');
    }
  };

  //загрузка пользователей
  const fetchUsers = async () => {
    try {
      const response = await adminAPI.getUsers();
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Ошибка загрузки пользователей');
    }
  };


  //загрузка заказов
  const fetchOrders = async () => {
    try {
      const response = await adminAPI.getAllOrders();
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Ошибка загрузки заказов');
    }
  };

  //загрузка курьеров
  const fetchCouriers = async () => {
    try {
      const response = await couriersAPI.getAll();
      setCouriers(response.data.couriers || []);
    } catch (error) {
      console.error('Ошибка загрузки курьеров');
    }
  };

  const createProduct = async (e) => {
    e.preventDefault(); //не перехагружать страницу
    setLoading(true); //загрузка
    try {
      await adminAPI.createProduct({
        id: parseInt(newProduct.id),
        name: newProduct.name,
        description: newProduct.description,
        price: parseFloat(newProduct.price),
        weight: parseFloat(newProduct.weight),
        category: newProduct.category
      });
      setMessage('Товар создан');
      setNewProduct({ id: '', name: '', description: '', price: '', weight: '', category: '' });
      fetchProducts(); //обновляем список товаров
    } catch (error) {
      setMessage('Ошибка создания товара ');
    }
    setLoading(false);
  };



  //отмена заказа
  const cancelOrder = async (orderId) => {
    if (!window.confirm('Отменить заказ?')) return;
    setLoading(true);
    try {
      await adminAPI.cancelOrder(orderId);
      setMessage(`Заказ ${orderId} отменён`);
      fetchOrders(); //обновить список заказов
    } catch (error) {
      setMessage('Ошибка отмены заказа');
    }
    setLoading(false);
  };


  //создани е курьера
  const createCourier = async (e) => {
    e.preventDefault(); //не перезагружаем страницу
    setLoading(true);
    try {
      await couriersAPI.create(newCourier);
      setMessage('Курьер создан');
      setNewCourier({
        username: '',
        email: '',
        password: '',
        courier_type: 'foot',
        regions: [1],
        working_hours: ['09:00-18:00']
      });
      fetchCouriers();
      fetchUsers();
    } catch (error) {
      setMessage('Ошибка создания курьера ');
    }
    setLoading(false);
  };




  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Админ-панель</h1>
        <button onClick={onLogout} style={styles.logoutButton}>Выйти</button>
      </div>

      {message && <div style={styles.message}>{message}</div>}


      {/*вкладки*/}
      <div style={styles.tabs}>
        <button onClick={() => setActiveTab('products')} style={{...styles.tab, ...(activeTab === 'products' ? styles.activeTab : {})}}>Товары</button>
        <button onClick={() => setActiveTab('users')} style={{...styles.tab, ...(activeTab === 'users' ? styles.activeTab : {})}}>Пользователи</button>
        <button onClick={() => setActiveTab('orders')} style={{...styles.tab, ...(activeTab === 'orders' ? styles.activeTab : {})}}>Заказы</button>
        <button onClick={() => setActiveTab('couriers')} style={{...styles.tab, ...(activeTab === 'couriers' ? styles.activeTab : {})}}>Курьеры</button>
        <button onClick={() => setActiveTab('createProduct')} style={{...styles.tab, ...(activeTab === 'createProduct' ? styles.activeTab : {})}}>Создать товар</button>
        <button onClick={() => setActiveTab('createCourier')} style={{...styles.tab, ...(activeTab === 'createCourier' ? styles.activeTab : {})}}>Создать курьера</button>
      </div>

      {/*товары */}
      {activeTab === 'products' && (
        <div style={styles.section}>
          <h2>Все товары</h2>
          <div style={styles.grid}>
            {products.map(product => (
              <div key={product.id} style={styles.card}>
                <h3>{product.name}</h3>
                <p><strong>ID:</strong> {product.id}</p>
                <p><strong>Цена:</strong> {product.price} ₽</p>
                <p><strong>Вес:</strong> {product.weight} кг</p>
                <p><strong>Категория:</strong> {product.category}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/*пользователи */}
      {activeTab === 'users' && (
        <div style={styles.section}>
          <h2>Пользователи</h2>
          <div style={styles.grid}>
            {users.map(user => (
              <div key={user.id} style={styles.card}>
                <h3>{user.username}</h3>
                <p><strong>ID:</strong> {user.id}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Роль:</strong> {user.role}</p>
                <p><strong>Регион:</strong> {user.region || '-'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/*заказы */}
      {activeTab === 'orders' && (
        <div style={styles.section}>
          <h2>Все заказы</h2>
          <div style={styles.ordersList}>
            {orders.map(order => (
              <div key={order.order_id} style={styles.orderCard}>
                <p><strong>Заказ #{order.order_id}</strong></p>
                <p>Статус: {order.status}</p>
                <p>Сумма: {order.total_price} ₽</p>
                <p>Вес: {order.weight} кг</p>
                <p>Регион: {order.region}</p>
                {order.status !== 'completed' && order.status !== 'cancelled' && (
                  <button onClick={() => cancelOrder(order.order_id)} style={styles.cancelButton}>❌ Отменить</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/*курьеры */}
      {activeTab === 'couriers' && (
        <div style={styles.section}>
          <h2>Курьеры</h2>
          <div style={styles.grid}>
            {couriers.map(courier => (
              <div key={courier.courier_id} style={styles.card}>
                <h3>Курьер #{courier.courier_id}</h3>
                <p><strong>Тип:</strong> {courier.courier_type}</p>
                <p><strong>Регионы:</strong> {courier.regions?.join(', ')}</p>
                <p><strong>Часы работы:</strong> {courier.working_hours?.join(', ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/*создание товара */}
      {activeTab === 'createProduct' && (
        <div style={styles.section}>
          <h2>Создать товар</h2>
          <form onSubmit={createProduct} style={styles.form}>
            <input type="number" placeholder="ID товара" value={newProduct.id} onChange={e => setNewProduct({...newProduct, id: e.target.value})} required style={styles.input} />
            <input type="text" placeholder="Название" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} required style={styles.input} />
            <textarea placeholder="Описание" value={newProduct.description} onChange={e => setNewProduct({...newProduct, description: e.target.value})} style={styles.textarea} />
            <input type="number" placeholder="Цена" value={newProduct.price} onChange={e => setNewProduct({...newProduct, price: e.target.value})} required style={styles.input} />
            <input type="number" placeholder="Вес" step="0.1" value={newProduct.weight} onChange={e => setNewProduct({...newProduct, weight: e.target.value})} required style={styles.input} />
            <input type="text" placeholder="Категория" value={newProduct.category} onChange={e => setNewProduct({...newProduct, category: e.target.value})} style={styles.input} />
            <button type="submit" disabled={loading} style={styles.button}>Создать товар</button>
          </form>
        </div>
      )}

      {/*создание курьера */}
      {activeTab === 'createCourier' && (
        <div style={styles.section}>
          <h2>Создать курьера</h2>
          <form onSubmit={createCourier} style={styles.form}>
            <input type="text" placeholder="Имя пользователя" value={newCourier.username} onChange={e => setNewCourier({...newCourier, username: e.target.value})} required style={styles.input} />
            <input type="email" placeholder="Email" value={newCourier.email} onChange={e => setNewCourier({...newCourier, email: e.target.value})} required style={styles.input} />
            <input type="password" placeholder="Пароль" value={newCourier.password} onChange={e => setNewCourier({...newCourier, password: e.target.value})} required style={styles.input} />
            <select value={newCourier.courier_type} onChange={e => setNewCourier({...newCourier, courier_type: e.target.value})} style={styles.input}>
              <option value="foot">Пеший</option>
              <option value="bike">Велосипед</option>
              <option value="car">Автомобиль</option>
            </select>
            <input type="text" placeholder="Регионы (через запятую, например: 1,2,3)" onChange={e => setNewCourier({...newCourier, regions: e.target.value.split(',').map(Number)})} style={styles.input} />
            <input type="text" placeholder="Часы работы (например: 09:00-18:00)" onChange={e => setNewCourier({...newCourier, working_hours: [e.target.value]})} style={styles.input} />
            <button type="submit" disabled={loading} style={styles.button}>Создать курьера</button>
          </form>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: '20px', maxWidth: '1400px', margin: '0 auto', fontFamily: 'Arial, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  title: { margin: 0 },
  logoutButton: { backgroundColor: '#6c757d', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  message: { padding: '10px', backgroundColor: '#d4edda', color: '#155724', borderRadius: '4px', marginBottom: '20px' },
  tabs: { display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' },
  tab: { padding: '10px 20px', backgroundColor: '#f0f0f0', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
  activeTab: { backgroundColor: '#007bff', color: 'white' },
  section: { backgroundColor: '#f9f9f9', padding: '20px', borderRadius: '8px', marginTop: '20px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px', marginTop: '15px' },
  card: { backgroundColor: 'white', padding: '15px', borderRadius: '8px', border: '1px solid #ddd', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  ordersList: { display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' },
  orderCard: { backgroundColor: '#bbdef5', padding: '15px', borderRadius: '8px', border: '1px solid #ddd' },
  cancelButton: { backgroundColor: '#6c757d', color: 'black', padding: '5px 10px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' },
  form: { display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '500px' },
  input: { padding: '10px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '16px' },
  textarea: { padding: '10px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '16px', minHeight: '80px' },
  button: { backgroundColor: '#bbdef5', color: 'white', padding: '10px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }
};

export default AdminPage;