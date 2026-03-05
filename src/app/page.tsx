import {
  Package,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  Users,
  Settings,
} from "lucide-react";

// Mock data for now - will connect to API later
const stats = [
  {
    title: "Total Products",
    value: "1,234",
    change: "+12%",
    icon: Package,
    color: "blue",
  },
  {
    title: "Low Stock Items",
    value: "23",
    change: "+5%",
    icon: AlertTriangle,
    color: "orange",
  },
  {
    title: "Inventory Value",
    value: "₱45,231",
    change: "+8%",
    icon: DollarSign,
    color: "green",
  },
  {
    title: "Active Users",
    value: "12",
    change: "+2",
    icon: Users,
    color: "purple",
  },
];

const recentProducts = [
  { id: 1, name: "Wireless Mouse", sku: "MOU-001", stock: 45, status: "In Stock" },
  { id: 2, name: "Mechanical Keyboard", sku: "KEY-002", stock: 12, status: "Low Stock" },
  { id: 3, name: "USB-C Cable", sku: "CAB-003", stock: 0, status: "Out of Stock" },
  { id: 4, name: "Monitor 27\"", sku: "MON-004", stock: 8, status: "Low Stock" },
  { id: 5, name: "Webcam HD", sku: "CAM-005", stock: 23, status: "In Stock" },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Welcome back! Here&apos;s what&apos;s happening with your inventory.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const colorClasses = {
            blue: "bg-blue-50 text-blue-600",
            orange: "bg-orange-50 text-orange-600",
            green: "bg-green-50 text-green-600",
            purple: "bg-purple-50 text-purple-600",
          }[stat.color];

          return (
            <div
              key={stat.title}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {stat.value}
                  </p>
                  <p className="text-sm text-green-600 mt-1">{stat.change}</p>
                </div>
                <div className={`p-3 rounded-lg ${colorClasses}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Products Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Recent Products
            </h2>
            <a
              href="/products"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              View All →
            </a>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {recentProducts.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {product.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {product.sku}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {product.stock}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        product.status === "In Stock"
                          ? "bg-green-100 text-green-700"
                          : product.status === "Low Stock"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {product.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a
          href="/products/new"
          className="bg-blue-600 hover:bg-blue-700 text-white p-6 rounded-xl transition-colors"
        >
          <Package className="w-8 h-8 mb-3" />
          <h3 className="font-semibold">Add New Product</h3>
          <p className="text-blue-100 text-sm mt-1">
            Create a new inventory item
          </p>
        </a>
        <a
          href="/reports"
          className="bg-white hover:bg-gray-50 border border-gray-200 p-6 rounded-xl transition-colors"
        >
          <TrendingUp className="w-8 h-8 mb-3 text-gray-600" />
          <h3 className="font-semibold text-gray-900">View Reports</h3>
          <p className="text-gray-500 text-sm mt-1">
            Analyze inventory trends
          </p>
        </a>
        <a
          href="/settings"
          className="bg-white hover:bg-gray-50 border border-gray-200 p-6 rounded-xl transition-colors"
        >
          <Settings className="w-8 h-8 mb-3 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Settings</h3>
          <p className="text-gray-500 text-sm mt-1">
            Manage system preferences
          </p>
        </a>
      </div>
    </div>
  );
}
