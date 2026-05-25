import { api } from '../api'

export const listCategories = () =>
  api.get('/categories').then((r) => r.data)

export const getCategoryTree = () =>
  api.get('/categories/tree').then((r) => r.data)

export const createCategory = (data) =>
  api.post('/categories', data).then((r) => r.data)

export const updateCategory = (id, data) =>
  api.put(`/categories/${id}`, data).then((r) => r.data)

export const deleteCategory = (id) =>
  api.delete(`/categories/${id}`)
