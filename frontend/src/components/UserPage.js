import React, { useState, useEffect } from 'react';
import { productsAPI, cartAPI, ordersAPI } from '../services/api';

function UserPage({ onLogout }) {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [cart, setCart] = useState({ items: [], total_price: 0, total_weight: 0 });
  const [orderResult, setOrderResult] = useState(null);
  const [cartJson, setCartJson] = useState('');
  const [orderJson, setOrderJson] = useState('');
  const [loading, setLoading] = useState(false);

   const [region, setRegion] = useState('');
  const [address, setAddress] = useState('');
  const [deliveryHours, setDeliveryHours] = useState('10:00-18:00');


  //загрузка товаров и корзины
  useEffect(() => {
    fetchProducts();
    fetchCart();
  }, []);


  //загрузка товара
  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getAll();
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Ошибка загрузки товаров');
    }
  };

  //загрузка корзины
  const fetchCart = async () => {
    try {
      const response = await cartAPI.getCart();
      setCart(response.data);
      setCartJson(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error('Ошибка загрузки корзины');
    }
  };

  //добавление товара в корзимну
  const addToCart = async (productId) => {
    setLoading(true);
    try {
      await cartAPI.add(productId, 1); //добавление 1 штуки
      await fetchCart();
      alert('Товар добавлен в корзину');
    } catch (error) {
      console.error('Ошибка добавления товара');
      alert('Ошибка добавления товара');
    }
    setLoading(false);
  };


 //оформление заказа
const checkout = async () => {
  setLoading(true);
  try {
    if (!region || !address || !deliveryHours) {
      alert('Пожалуйста, заполните все поля доставки');
      setLoading(false);
      return;
    }

    const orderData = {
      region: parseInt(region),
      address: address,
      delivery_hours: [deliveryHours]   // deliveryHours уже в правильном формате
    };
    
    console.log('Отправляем:', JSON.stringify(orderData, null, 2));
    
    const response = await ordersAPI.checkout(orderData);
    setOrderResult(response.data);
    setOrderJson(JSON.stringify(response.data, null, 2));
    await fetchCart();
    alert('Заказ оформлен!');
    
    setRegion('');
    setAddress('');
    setDeliveryHours('');
  } catch (error) {
    console.error('Ошибка:', error.response?.data);
    
    let errorMsg = 'Ошибка оформления заказа';
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail;
    }
    alert(errorMsg);
  }
  setLoading(false);
};



  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Мой магазин</h1>
        <button onClick={onLogout} style={styles.logoutButton}>Выйти</button>
      </div>
      
      {/*секция товаров */}
      <div style={styles.section}>
        <h2>Товары</h2>
        <div style={styles.productsGrid}>
          {products.map(product => (
            <div key={product.id} style={styles.productCard}>
              <h3>{product.name}</h3>
              <p><strong>ID:</strong> {product.id}</p>
              <p><strong>Цена:</strong> {product.price} ₽</p>
              <p><strong>Вес:</strong> {product.weight} кг</p>
              <button onClick={() => addToCart(product.id)} style={styles.button} disabled={loading}>
                Добавить
              </button>
              <button onClick={() => setSelectedProduct(product)} style={styles.viewButton}>
                Подробнее
              </button>
            </div>
          ))}
        </div>
      </div>

      {/*окно с деталями */}
      {selectedProduct && (
        <div style={styles.modal} onClick={() => setSelectedProduct(null)}>
          <div style={styles.modalContent} onClick={e => e.stopPropagation()}>
            <h2>{selectedProduct.name}</h2>
            <p><strong>ID:</strong> {selectedProduct.id}</p>
            <p><strong>Описание:</strong> {selectedProduct.description}</p>
            <p><strong>Цена:</strong> {selectedProduct.price} ₽</p>
            <p><strong>Вес:</strong> {selectedProduct.weight} кг</p>
            <p><strong>Категория:</strong> {selectedProduct.category}</p>
            <button onClick={() => setSelectedProduct(null)} style={styles.closeButton}>Закрыть</button>
          </div>
        </div>
      )}



{/*данные для доставки */}
      <div style={styles.section}>
        <h2>Данные для доставки</h2>
        <div style={styles.deliveryForm}>
          
          {/*регион*/}
          <div style={styles.formGroup}>
            <label style={styles.label}>Регион:</label>
            <select 
              value={region} 
              onChange={(e) => setRegion(e.target.value)}
              style={styles.select}
              required
            >
              <option value="">Выберите регион</option>
              <option value="1">Регион 1</option>
              <option value="2">Регион 2</option>
              <option value="3">Регион 3</option>
              <option value="4">Регион 4</option>
              <option value="5">Регион 5</option>
            </select>
          </div>

          {/*адрес*/}
          <div style={styles.formGroup}>
            <label style={styles.label}>Адрес доставки:</label>
            <input
              type="text"
              placeholder="Город, улица, дом, квартира"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              style={styles.input}
              required
            />
          </div>

          {/*время */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Время доставки:</label>
            <select 
              value={deliveryHours} 
              onChange={(e) => setDeliveryHours(e.target.value)}
              style={styles.select}
              required
            >
              <option value="">Выберите время</option>
              <option value="09:00-12:00">09:00 - 12:00</option>
              <option value="12:00-15:00">12:00 - 15:00</option>
              <option value="15:00-17:00">15:00 - 17:00</option>
              <option value="17:00-19:00">17:00 - 19:00</option>
              <option value="19:00-21:00">19:00 - 21:00</option>
              <option value="21:00-23:00">21:00 - 23:00</option>
            </select>
          </div>
        </div>
      </div>


      
      {/*корзина*/}
      <div style={styles.section}>
        <h2>Корзина</h2>
        <div style={styles.jsonBox}>
          <pre style={styles.jsonPre}>{cartJson || 'Корзина пуста'}</pre>
        </div>
        <div style={styles.cartSummary}>
          <p><strong>Итого:</strong> {cart.total_price} ₽</p>
          <p><strong>Общий вес:</strong> {cart.total_weight} кг</p>
          <button onClick={checkout} style={styles.checkoutButton} disabled={loading}>
            Оформить заказ
          </button>
        </div>
      </div>

      {/*заказ*/}
      <div style={styles.section}>
        <h2>Последний заказ</h2>
        <div style={styles.jsonBox}>
          <pre style={styles.jsonPre}>{orderJson || 'Нет заказов'}</pre>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px'
  },
  title: {
    textAlign: 'center',
    color: '#333',
    margin: 0
  },
  logoutButton: {
    backgroundColor: '#6c757d',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  section: {
    marginBottom: '40px',
    padding: '20px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#f9f9f9'
  },
  productsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '20px',
    marginTop: '20px'
  },
  productCard: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  button: {
    backgroundColor: '#87CEEB',
    color: 'white',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginRight: '10px',
    marginTop: '10px'
  },
  viewButton: {
    backgroundColor: '#2196F3',
    color: 'white',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '10px'
  },
  checkoutButton: {
    backgroundColor: '#87CEEB',
    color: 'white',
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    marginTop: '10px'
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  modalContent: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '8px',
    maxWidth: '500px',
    width: '90%'
  },
  closeButton: {
    backgroundColor: '#6c757d',
    color: 'white',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '10px'
  },
  jsonBox: {
    backgroundColor: '#2d2d2d',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
    overflowX: 'auto'
  },
  jsonPre: {
    color: '#f8f8f2',
    margin: 0,
    fontSize: '12px',
    fontFamily: 'monospace'
  },
  cartSummary: {
    padding: '15px',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
    textAlign: 'center'
  }
};

export default UserPage;