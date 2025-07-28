import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign, 
  FileText, 
  Users, 
  CheckCircle,
  AlertTriangle,
  Clock,
  MapPin,
  Eye,
  Download
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Mock data - in real app, this would come from API
  useEffect(() => {
    setTimeout(() => {
      setStats({
        overview: {
          total_reports: 1247,
          verified_reports: 1109,
          pending_reports: 89,
          disputed_reports: 49,
          verification_rate: "89.1%"
        },
        financial_impact: {
          estimated_fraud_exposed: 2500000000, // 2.5B Naira
          high_risk_reports: 23,
          potential_savings: 2000000000 // 2B Naira
        },
        geographic_distribution: [
          { state: 'Lagos', reports_count: 234, total_budget: 450000000 },
          { state: 'Abuja', reports_count: 189, total_budget: 380000000 },
          { state: 'Kano', reports_count: 156, total_budget: 290000000 },
          { state: 'Rivers', reports_count: 134, total_budget: 250000000 },
          { state: 'Ogun', reports_count: 98, total_budget: 180000000 }
        ],
        project_types: [
          { project_type: 'school', count: 345 },
          { project_type: 'road', count: 298 },
          { project_type: 'clinic', count: 234 },
          { project_type: 'water_project', count: 189 },
          { project_type: 'bridge', count: 98 },
          { project_type: 'market', count: 83 }
        ],
        recent_activity: [
          {
            id: '1',
            project_name: 'Ikeja Primary School Block B',
            state: 'Lagos',
            status: 'verified',
            created_at: '2024-01-15T10:30:00Z',
            verification_score: 92
          },
          {
            id: '2',
            project_name: 'Abuja-Kaduna Highway Section 3',
            state: 'FCT',
            status: 'under_review',
            created_at: '2024-01-15T09:15:00Z',
            verification_score: 78
          },
          {
            id: '3',
            project_name: 'Kano General Hospital Wing',
            state: 'Kano',
            status: 'disputed',
            created_at: '2024-01-15T08:45:00Z',
            verification_score: 45
          }
        ]
      })
      setLoading(false)
    }, 1000)
  }, [])

  const formatCurrency = (amount) => {
    if (amount >= 1000000000) {
      return `₦${(amount / 1000000000).toFixed(1)}B`
    } else if (amount >= 1000000) {
      return `₦${(amount / 1000000).toFixed(1)}M`
    } else {
      return `₦${amount.toLocaleString()}`
    }
  }

  const getStatusColor = (status) => {
    switch(status) {
      case 'verified': return 'bg-green-100 text-green-800'
      case 'under_review': return 'bg-yellow-100 text-yellow-800'
      case 'disputed': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch(status) {
      case 'verified': return <CheckCircle className="h-4 w-4" />
      case 'under_review': return <Clock className="h-4 w-4" />
      case 'disputed': return <AlertTriangle className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#6B7280']

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="h-64 bg-gray-200 rounded-lg"></div>
              <div className="h-64 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-2">Monitor corruption reports and transparency metrics across Nigeria</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            <Button size="sm">
              <Eye className="h-4 w-4 mr-2" />
              Live View
            </Button>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.overview.total_reports.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12% from last month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Verification Rate</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.overview.verification_rate}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +2.3% from last month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Fraud Exposed</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.financial_impact.estimated_fraud_exposed)}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-red-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +₦340M this month
                </span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12,847</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8% from last month
                </span>
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Geographic Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Reports by State</CardTitle>
              <CardDescription>Top 5 states with most corruption reports</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.geographic_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="state" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'reports_count' ? value : formatCurrency(value),
                      name === 'reports_count' ? 'Reports' : 'Budget'
                    ]}
                  />
                  <Bar dataKey="reports_count" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Project Types */}
          <Card>
            <CardHeader>
              <CardTitle>Project Types</CardTitle>
              <CardDescription>Distribution of reported project categories</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.project_types}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ project_type, percent }) => `${project_type} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {stats.project_types.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest corruption reports and their verification status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recent_activity.map((report) => (
                <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getStatusIcon(report.status)}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{report.project_name}</h4>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <MapPin className="h-3 w-3" />
                        <span>{report.state}</span>
                        <span>•</span>
                        <span>{new Date(report.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-sm font-medium">Score: {report.verification_score}%</div>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${report.verification_score}%` }}
                        ></div>
                      </div>
                    </div>
                    <Badge className={getStatusColor(report.status)}>
                      {report.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard

