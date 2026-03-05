"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Loader2 } from "lucide-react";
import { Navigation } from "@/components/Navigation";

interface Category {
  id: number;
  name: string;
  color: string;
}

export default function NewProductPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: "",
    sku: "",
    description: "",
    categoryId: "",
    unitPrice: "",
    currentStock: "",
    minStockLevel: "",
    barcode: "",
  });

  useEffect(() => {
    fetchCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/categories/all?is_active=true`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch categories");
      }

      const data = await response.json();
      setCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load categories");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }

      const productData = {
        name: formData.name,
        sku: formData.sku,
        description: formData.description || null,
        category_id: formData.categoryId ? parseInt(formData.categoryId) : null,
        unit_price: parseFloat(formData.unitPrice),
        current_stock: parseInt(formData.currentStock) || 0,
        min_stock_level: parseInt(formData.minStockLevel) || 0,
        barcode: formData.barcode || null,
      };

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/products`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(productData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create product");
      }

      router.push("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create product");
      setSaving(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="ml-64 p-8">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="ml-64 p-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Link
              href="/products"
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Add New Product</h1>
              <p className="text-gray-600 mt-1">
                Create a new inventory item
              </p>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Product Name */}
                <div className="md:col-span-2">
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Product Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter product name"
                    value={formData.name}
                    onChange={handleChange}
                  />
                </div>

                {/* SKU */}
                <div>
                  <label
                    htmlFor="sku"
                    className="block text-sm font-medium text-gray-700"
                  >
                    SKU <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="sku"
                    name="sku"
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., PROD-001"
                    value={formData.sku}
                    onChange={handleChange}
                  />
                </div>

                {/* Category */}
                <div>
                  <label
                    htmlFor="categoryId"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Category
                  </label>
                  <select
                    id="categoryId"
                    name="categoryId"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={formData.categoryId}
                    onChange={handleChange}
                  >
                    <option value="">Select a category</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  <div className="mt-1">
                    <Link
                      href="/categories"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Manage categories →
                    </Link>
                  </div>
                </div>

                {/* Unit Price */}
                <div>
                  <label
                    htmlFor="unitPrice"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Unit Price <span className="text-red-500">*</span>
                  </label>
                  <div className="mt-1 relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                      ₱
                    </span>
                    <input
                      type="number"
                      id="unitPrice"
                      name="unitPrice"
                      required
                      min="0"
                      step="0.01"
                      className="block w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.00"
                      value={formData.unitPrice}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                {/* Barcode */}
                <div>
                  <label
                    htmlFor="barcode"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Barcode
                  </label>
                  <input
                    type="text"
                    id="barcode"
                    name="barcode"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 123456789012"
                    value={formData.barcode}
                    onChange={handleChange}
                  />
                </div>

                {/* Current Stock */}
                <div>
                  <label
                    htmlFor="currentStock"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Current Stock
                  </label>
                  <input
                    type="number"
                    id="currentStock"
                    name="currentStock"
                    min="0"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                    value={formData.currentStock}
                    onChange={handleChange}
                  />
                </div>

                {/* Min Stock Level */}
                <div>
                  <label
                    htmlFor="minStockLevel"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Min Stock Level
                  </label>
                  <input
                    type="number"
                    id="minStockLevel"
                    name="minStockLevel"
                    min="0"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                    value={formData.minStockLevel}
                    onChange={handleChange}
                  />
                </div>

                {/* Description */}
                <div className="md:col-span-2">
                  <label
                    htmlFor="description"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter product description"
                    value={formData.description}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-4">
              <Link
                href="/products"
                className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Product
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
