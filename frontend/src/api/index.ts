import api from './client'

export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const productApi = {
  list: (page = 1) => api.get('/products', { params: { page } }),
  get: (id: number) => api.get(`/products/${id}`),
  search: (params: Record<string, any>) => api.get('/products/search', { params }),
  create: (data: any) => api.post('/products', data),
}

export const orderApi = {
  create: (items: { product_id: number; quantity: number }[]) =>
    api.post('/orders', { items }),
  list: () => api.get('/orders'),
}

export const recommendApi = {
  home: () => api.get('/recommend/home'),
  similar: (productId: number) => api.get(`/recommend/similar/${productId}`),
  forYou: () => api.get('/recommend/for-you'),
}

export const adApi = {
  fetch: () => api.get('/ads/fetch'),
  impression: (data: { ad_id: number; impression_type: string }) =>
    api.post('/ads/impression', data),
  create: (data: any) => api.post('/ads', data),
  my: () => api.get('/ads/my'),
  stats: (id: number) => api.get(`/ads/${id}/stats`),
}

export const communityApi = {
  getReviews: (productId: number) => api.get(`/reviews/product/${productId}`),
  postReview: (data: { product_id: number; rating: number; content: string }) =>
    api.post('/reviews', data),
  helpful: (reviewId: number) => api.post(`/reviews/${reviewId}/helpful`),
  getQA: (productId: number) => api.get(`/qa/product/${productId}`),
  postQuestion: (data: { product_id: number; question: string }) =>
    api.post('/qa', data),
  answer: (qaId: number, data: { answer: string }) =>
    api.post(`/qa/${qaId}/answer`, data),
}

export const activityApi = {
  myScore: () => api.get('/activity/my-score'),
}

export const behaviorApi = {
  track: (data: { product_id?: number; behavior_type: string; context?: any }) =>
    api.post('/behavior/track', data),
}

export const analyticsApi = {
  dashboard: () => api.get('/analytics/dashboard'),
  activityDist: () => api.get('/analytics/activity-dist'),
  adPerformance: () => api.get('/analytics/ad-performance'),
}
