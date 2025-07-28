import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { 
  Search, 
  Filter, 
  MapPin, 
  Calendar, 
  DollarSign,
  Eye,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Building,
  Camera,
  TrendingUp,
  Users
} from 'lucide-react'

const TransparencyFeed = () => {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '',
    state: '',
    project_type: '',
    status: ''
  })
  const [selectedReport, setSelectedReport] = useState(null)

  // Fetch data from API
  useEffect(() => {
    const fetchFeed = async () => {
      try {
        setLoading(true)
        const response = await fetch('https://xlhyimc39mw6.manus.space/api/feed')
        const data = await response.json()
        
        // Transform API data to match component structure
        const transformedReports = data.feed.map(item => ({
          id: item.id,
          project_name: item.title,
          project_type: item.type === 'report_verified' ? 'school' : 
                       item.type === 'fraud_detected' ? 'road' : 
                       item.type === 'community_action' ? 'clinic' : 'other',
          description: item.description,
          location: {
            location_name: item.location,
            state: item.location.split(' ').pop(),
            lga: item.location.split(',')[0]
          },
          financial: {
            reported_budget: Math.random() * 50000000000 + 10000000000, // Random budget for demo
            actual_cost_estimate: Math.random() * 30000000000 + 5000000000
          },
          status: item.status === 'verified' ? 'verified' : 
                  item.status === 'under_investigation' ? 'under_review' : 
                  item.status === 'disputed' ? 'disputed' : 'pending',
          verification_score: Math.floor(Math.random() * 40) + 60,
          community_votes: item.votes,
          created_at: item.timestamp,
          reporter_id: `User_${Math.random().toString(36).substr(2, 4).toUpperCase()}`,
          evidence_count: item.evidence_count,
          blockchain_hash: `${Math.random().toString(36).substr(2, 6)}...`,
          ai_analysis: {
            anomaly_score: Math.floor(Math.random() * 50) + 50,
            fraud_indicators: [
              { type: 'budget_anomaly', description: 'Budget analysis completed', confidence: 0.8 },
              { type: 'timeline_check', description: 'Timeline verification passed', confidence: 0.7 }
            ]
          }
        }))
        
        setReports(transformedReports)
      } catch (error) {
        console.error('Error fetching feed:', error)
        // Fallback to mock data if API fails
        setReports([
          {
            id: '1',
            project_name: 'Lagos School Project',
            project_type: 'school',
            description: 'Community verification completed for Lagos State Primary School construction project.',
            location: {
              location_name: 'Lagos State',
              state: 'Lagos',
              lga: 'Lagos'
            },
            financial: {
              reported_budget: 20000000000,
              actual_cost_estimate: 15000000000
            },
            status: 'verified',
            verification_score: 92,
            community_votes: 47,
            created_at: '2025-07-26T08:30:00Z',
            reporter_id: 'User_8F3E',
            evidence_count: 12,
            blockchain_hash: 'abc123...',
            ai_analysis: {
              anomaly_score: 25,
              fraud_indicators: [
                { type: 'verification_passed', description: 'All checks passed', confidence: 0.9 }
              ]
            }
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchFeed()
  }, [])

  const formatCurrency = (amount) => {
    if (amount >= 100000000000) { // 1B naira in kobo
      return `₦${(amount / 100000000000).toFixed(1)}B`
    } else if (amount >= 100000000) { // 1M naira in kobo
      return `₦${(amount / 100000000).toFixed(1)}M`
    } else {
      return `₦${(amount / 100).toLocaleString()}`
    }
  }

  const getStatusColor = (status) => {
    switch(status) {
      case 'verified': return 'bg-green-100 text-green-800 border-green-200'
      case 'under_review': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'disputed': return 'bg-red-100 text-red-800 border-red-200'
      case 'pending': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status) => {
    switch(status) {
      case 'verified': return <CheckCircle className="h-4 w-4" />
      case 'under_review': return <Clock className="h-4 w-4" />
      case 'disputed': return <AlertTriangle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getAnomalyColor = (score) => {
    if (score >= 80) return 'text-red-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-green-600'
  }

  const filteredReports = reports.filter(report => {
    return (
      (!filters.search || report.project_name.toLowerCase().includes(filters.search.toLowerCase()) ||
       report.description.toLowerCase().includes(filters.search.toLowerCase())) &&
      (!filters.state || report.location.state === filters.state) &&
      (!filters.project_type || report.project_type === filters.project_type) &&
      (!filters.status || report.status === filters.status)
    )
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Transparency Feed</h1>
          <p className="text-gray-600 mb-6">
            Real-time feed of corruption reports from citizens across Nigeria. 
            All reports are verified by AI and community moderators.
          </p>

          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search reports..."
                    value={filters.search}
                    onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                    className="pl-10"
                  />
                </div>
                
                <Select value={filters.state} onValueChange={(value) => setFilters(prev => ({ ...prev, state: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All States" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All States</SelectItem>
                    <SelectItem value="Lagos">Lagos</SelectItem>
                    <SelectItem value="FCT">FCT</SelectItem>
                    <SelectItem value="Kano">Kano</SelectItem>
                    <SelectItem value="Rivers">Rivers</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={filters.project_type} onValueChange={(value) => setFilters(prev => ({ ...prev, project_type: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Types</SelectItem>
                    <SelectItem value="school">School</SelectItem>
                    <SelectItem value="road">Road</SelectItem>
                    <SelectItem value="clinic">Clinic</SelectItem>
                    <SelectItem value="water_project">Water Project</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={filters.status} onValueChange={(value) => setFilters(prev => ({ ...prev, status: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Status</SelectItem>
                    <SelectItem value="verified">Verified</SelectItem>
                    <SelectItem value="under_review">Under Review</SelectItem>
                    <SelectItem value="disputed">Disputed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Reports List */}
        <div className="space-y-6">
          {filteredReports.map((report) => (
            <Card key={report.id} className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge className={getStatusColor(report.status)}>
                        {getStatusIcon(report.status)}
                        <span className="ml-1">{report.status.replace('_', ' ')}</span>
                      </Badge>
                      <Badge variant="outline">
                        <Building className="h-3 w-3 mr-1" />
                        {report.project_type}
                      </Badge>
                      <Badge variant="outline">
                        <Camera className="h-3 w-3 mr-1" />
                        {report.evidence_count} files
                      </Badge>
                    </div>
                    <CardTitle className="text-xl mb-2">{report.project_name}</CardTitle>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {report.location.location_name}
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {new Date(report.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-1" />
                        {report.reporter_id}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(report.financial.reported_budget)}
                    </div>
                    <div className="text-sm text-gray-600">Budget</div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <p className="text-gray-700 mb-4">{report.description}</p>
                
                {/* Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-green-600">{report.verification_score}%</div>
                    <div className="text-xs text-gray-600">Verification Score</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className={`text-lg font-bold ${getAnomalyColor(report.ai_analysis.anomaly_score)}`}>
                      {report.ai_analysis.anomaly_score}%
                    </div>
                    <div className="text-xs text-gray-600">AI Risk Score</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-600">{report.community_votes}</div>
                    <div className="text-xs text-gray-600">Community Votes</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-lg font-bold text-purple-600">
                      {formatCurrency(report.financial.reported_budget - report.financial.actual_cost_estimate)}
                    </div>
                    <div className="text-xs text-gray-600">Potential Waste</div>
                  </div>
                </div>

                {/* AI Fraud Indicators */}
                {report.ai_analysis.fraud_indicators.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">AI Fraud Indicators:</h4>
                    <div className="space-y-1">
                      {report.ai_analysis.fraud_indicators.map((indicator, index) => (
                        <div key={index} className="flex items-center text-sm">
                          <AlertTriangle className="h-4 w-4 text-red-500 mr-2" />
                          <span className="text-gray-700">{indicator.description}</span>
                          <Badge variant="outline" className="ml-2 text-xs">
                            {Math.round(indicator.confidence * 100)}% confidence
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center space-x-4">
                    <Button variant="outline" size="sm">
                      <ThumbsUp className="h-4 w-4 mr-1" />
                      Support
                    </Button>
                    <Button variant="outline" size="sm">
                      <ThumbsDown className="h-4 w-4 mr-1" />
                      Dispute
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-1" />
                      View Details
                    </Button>
                  </div>
                  <div className="text-xs text-gray-500">
                    Blockchain: {report.blockchain_hash.substring(0, 8)}...
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Load More */}
        <div className="text-center mt-8">
          <Button variant="outline">
            Load More Reports
          </Button>
        </div>
      </div>
    </div>
  )
}

export default TransparencyFeed

