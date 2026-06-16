import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';


//аутентификация
export const authAPI = {
  login: (username, password) => axios.post(`${API_BASE_URL}/auth/login`, { username, password }),
  
  register: (userData) => axios.post(`${API_BASE_URL}/auth/register`, userData),
  
  logout: () => {
    const apiKey = localStorage.getItem('api_key'); 
    return axios.post(`${API_BASE_URL}/auth/logout`, {}, { 
      headers: { 'API-Token': apiKey }
    });
  },
};


//товары
export const productsAPI = {
  getAll: (search, category) => {
    let url = `${API_BASE_URL}/products`;
    const params = [];
    if (search) params.push(`search=${search}`);
    if (category) params.push(`category=${category}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    return axios.get(url, {
      headers: { 'API-Token': localStorage.getItem('api_key') }
    });
  },
  
  getById: (productId) => axios.get(`${API_BASE_URL}/products/${productId}`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  getCategories: () => axios.get(`${API_BASE_URL}/products/categories/all`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};



//корзина
export const cartAPI = {
  getCart: () => axios.get(`${API_BASE_URL}/cart`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  add: (productId, quantity = 1) => axios.post(`${API_BASE_URL}/cart/add?product_id=${productId}&quantity=${quantity}`, {}, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  update: (productId, quantity) => axios.patch(`${API_BASE_URL}/cart/update?product_id=${productId}&quantity=${quantity}`, {}, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  remove: (productId) => axios.delete(`${API_BASE_URL}/cart/remove/${productId}`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  clear: () => axios.delete(`${API_BASE_URL}/cart/clear`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};



//заказы
export const ordersAPI = {
  checkout: (orderData) => axios.post(`${API_BASE_URL}/orders/checkout`, orderData, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  getMyOrders: () => axios.get(`${API_BASE_URL}/orders/my`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  
  getMyOrderDetail: (orderId) => axios.get(`${API_BASE_URL}/orders/my/${orderId}`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};


//админ
export const adminAPI = {
  getUsers: () => axios.get(`${API_BASE_URL}/admin/users`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  getAllOrders: () => axios.get(`${API_BASE_URL}/admin/orders`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  cancelOrder: (orderId) => axios.patch(`${API_BASE_URL}/admin/orders/${orderId}/cancel`, {}, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  createProduct: (product) => axios.post(`${API_BASE_URL}/admin/products`, product, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};

//курьеры админ
export const couriersAPI = {
  getAll: () => axios.get(`${API_BASE_URL}/couriers`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  create: (data) => axios.post(`${API_BASE_URL}/couriers`, data, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  delete: (courierId) => axios.delete(`${API_BASE_URL}/couriers/${courierId}`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};



//курьер
export const courierAPI = {
  getProfile: () => axios.get(`${API_BASE_URL}/courier/me`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  getAvailableOrders: () => axios.get(`${API_BASE_URL}/courier/orders/available`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  getMyOrders: () => axios.get(`${API_BASE_URL}/courier/orders/my`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  takeOrder: (orderId) => axios.post(`${API_BASE_URL}/courier/orders/take/${orderId}`, {}, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  completeOrder: (orderId) => axios.post(`${API_BASE_URL}/courier/orders/complete/${orderId}`, {}, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  getEarnings: () => axios.get(`${API_BASE_URL}/courier/earnings`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
  getRating: () => axios.get(`${API_BASE_URL}/courier/rating`, {
    headers: { 'API-Token': localStorage.getItem('api_key') }
  }),
};