/// <reference types="vite/client" />
import axios, { AxiosError } from "axios"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

// Attach the signed session cookie automatically (withCredentials: true handles cookies).
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Session expired — let the page handle redirect.
      window.dispatchEvent(new Event("auth:expired"))
    }
    return Promise.reject(error)
  }
)
