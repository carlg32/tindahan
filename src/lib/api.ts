"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Helper to get auth token from localStorage
function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  // Add auth token if available
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API request failed: ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// Authentication API
export const authApi = {
  login: (username: string, password: string) =>
    apiRequest<{ access_token: string; token_type: string; user: { id: number; username: string; role: string } }>(
      "/auth/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username, password }),
      }
    ),

  getMe: () =>
    apiRequest<{ id: number; username: string; role: string; is_active: boolean }>("/auth/me"),
};

// Products API
export const productsApi = {
  getAll: (params?: { page?: number; page_size?: number; search?: string; category?: string; low_stock?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.page_size) searchParams.append("page_size", params.page_size.toString());
    if (params?.search) searchParams.append("search", params.search);
    if (params?.category) searchParams.append("category", params.category);
    if (params?.low_stock) searchParams.append("low_stock", "true");
    
    return apiRequest<{
      items: Array<{
        id: number;
        sku: string;
        name: string;
        description: string | null;
        category: string | null;
        unit_price: string;
        current_stock: number;
        min_stock_level: number;
        barcode: string | null;
        is_active: boolean;
        is_low_stock: boolean;
        created_at: string;
      }>;
      total: number;
      page: number;
      page_size: number;
      pages: number;
    }>(`/products?${searchParams.toString()}`);
  },

  getById: (id: number) =>
    apiRequest<{
      id: number;
      sku: string;
      name: string;
      description: string | null;
      category: string | null;
      unit_price: string;
      current_stock: number;
      min_stock_level: number;
      barcode: string | null;
      is_active: boolean;
      is_low_stock: boolean;
      created_at: string;
    }>(`/products/${id}`),

  create: (data: {
    sku: string;
    name: string;
    description?: string;
    category?: string;
    unit_price: number;
    current_stock?: number;
    min_stock_level?: number;
    barcode?: string;
    is_active?: boolean;
  }) =>
    apiRequest<{
      id: number;
      sku: string;
      name: string;
      description: string | null;
      category: string | null;
      unit_price: string;
      current_stock: number;
      min_stock_level: number;
      barcode: string | null;
      is_active: boolean;
      is_low_stock: boolean;
      created_at: string;
    }>("/products", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<{
    name: string;
    description: string;
    category: string;
    unit_price: number;
    min_stock_level: number;
    barcode: string;
    is_active: boolean;
  }>) =>
    apiRequest<{
      id: number;
      sku: string;
      name: string;
      description: string | null;
      category: string | null;
      unit_price: string;
      current_stock: number;
      min_stock_level: number;
      barcode: string | null;
      is_active: boolean;
      is_low_stock: boolean;
      created_at: string;
    }>(`/products/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiRequest<void>(`/products/${id}`, {
      method: "DELETE",
    }),
};

// Dashboard API
export const dashboardApi = {
  getStats: () =>
    apiRequest<{
      total_products: number;
      active_products: number;
      low_stock_count: number;
      out_of_stock_count: number;
      total_inventory_value: number;
      movements_today: number;
      stock_in_today: number;
      stock_out_today: number;
      movements_this_week: number;
      stock_in_week: number;
      stock_out_week: number;
      total_users: number;
      active_users: number;
      products_by_category: Record<string, number>;
      last_updated: string;
    }>("/dashboard/stats"),

  getLowStockAlerts: () =>
    apiRequest<{
      alerts: Array<{
        product_id: number;
        sku: string;
        name: string;
        category: string | null;
        current_stock: number;
        min_stock_level: number;
        deficit: number;
        unit_price: number;
      }>;
      total_alerts: number;
      total_deficit_value: number;
    }>("/dashboard/low-stock-alerts"),
};