import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Shield, 
  Eye, 
  Users, 
  TrendingUp, 
  MapPin, 
  Camera, 
  Phone,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  FileText,
  Search
} from 'lucide-react'
import './App.css'

// Components
import Header from './components/Header'
import Hero from './components/Hero'
import Dashboard from './components/Dashboard'
import ReportForm from './components/ReportForm'
import TransparencyFeed from './components/TransparencyFeed'
import USSDSimulator from './components/USSDSimulator'
import AuthPages from './components/AuthPages'

function App() {
  const [currentView, setCurrentView] = useState('home')

  const renderCurrentView = () => {
    switch(currentView) {
      case 'dashboard':
        return <Dashboard />
      case 'report':
        return <ReportForm />
      case 'transparency':
        return <TransparencyFeed />
      case 'ussd':
        return <USSDSimulator />
      case 'login':
      case 'signup':
        return <AuthPages activeTab={currentView} setActiveTab={setCurrentView} />
      default:
        return <HomePage />
    }
  }

  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <Hero setCurrentView={setCurrentView} />
      
      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Fighting Corruption Through Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              GovTracka empowers Nigerian citizens to monitor government projects, 
              report irregularities, and ensure transparency in public spending.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <Card className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Camera className="h-12 w-12 text-green-600 mb-4" />
                <CardTitle>Photo Verification</CardTitle>
                <CardDescription>
                  Upload geotagged photos of government projects with AI-powered verification
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• GPS coordinate validation</li>
                  <li>• Blockchain evidence storage</li>
                  <li>• Automatic face anonymization</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Phone className="h-12 w-12 text-blue-600 mb-4" />
                <CardTitle>USSD Access</CardTitle>
                <CardDescription>
                  Report projects via *347*# - no internet required for feature phones
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Works on any mobile phone</li>
                  <li>• Voice note descriptions</li>
                  <li>• SMS status updates</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <Shield className="h-12 w-12 text-purple-600 mb-4" />
                <CardTitle>NDPA 2023 Compliant</CardTitle>
                <CardDescription>
                  Full compliance with Nigeria Data Protection Act 2023
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Data stored in Nigeria</li>
                  <li>• Right to be forgotten (*347*9#)</li>
                  <li>• Automatic anonymization</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Stats Section */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
            <h3 className="text-2xl font-bold text-center mb-8">Impact So Far</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">₦2.5B</div>
                <div className="text-sm text-gray-600">Fraud Exposed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">1,247</div>
                <div className="text-sm text-gray-600">Reports Submitted</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">89%</div>
                <div className="text-sm text-gray-600">Verification Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">15</div>
                <div className="text-sm text-gray-600">States Covered</div>
              </div>
            </div>
          </div>

          {/* How It Works */}
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-8">How It Works</h3>
            <div className="grid md:grid-cols-4 gap-8">
              <div className="flex flex-col items-center">
                <div className="bg-green-100 rounded-full p-4 mb-4">
                  <Camera className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="font-semibold mb-2">1. Report</h4>
                <p className="text-sm text-gray-600">Take photos of projects and submit via web or USSD</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="bg-blue-100 rounded-full p-4 mb-4">
                  <Eye className="h-8 w-8 text-blue-600" />
                </div>
                <h4 className="font-semibold mb-2">2. Verify</h4>
                <p className="text-sm text-gray-600">AI and community moderators verify submissions</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="bg-purple-100 rounded-full p-4 mb-4">
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
                <h4 className="font-semibold mb-2">3. Engage</h4>
                <p className="text-sm text-gray-600">Community votes and NGO partners investigate</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="bg-orange-100 rounded-full p-4 mb-4">
                  <TrendingUp className="h-8 w-8 text-orange-600" />
                </div>
                <h4 className="font-semibold mb-2">4. Impact</h4>
                <p className="text-sm text-gray-600">Public transparency drives government action</p>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl p-8 text-center text-white">
            <h3 className="text-3xl font-bold mb-4">Ready to Fight Corruption?</h3>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of Nigerians holding government accountable
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                variant="secondary"
                onClick={() => setCurrentView('report')}
                className="bg-white text-green-600 hover:bg-gray-100"
              >
                Report a Project
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                onClick={() => setCurrentView('transparency')}
                className="border-white text-white hover:bg-white hover:text-green-600"
              >
                View Reports
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer with NDPC Certification */}
      <footer className="govtracka-footer">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <p className="text-lg font-semibold mb-2">GovTracka - Citizen-Led Transparency Platform</p>
            <p className="text-gray-300 mb-4">Empowering Nigerians to fight corruption through technology</p>
            <div className="ndpc-badge">
              <Shield className="h-5 w-5 mr-2" />
              NDPC Certified - NDPA 2023 Compliant
            </div>
            <div className="mt-6 text-sm text-gray-400">
              <p>Data Protection Officer: dpo@govtracka.ng | Emergency: *347*9# for data deletion</p>
              <p className="mt-2">© 2025 GovTracka Nigeria Limited. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentView={currentView} setCurrentView={setCurrentView} />
      {renderCurrentView()}
    </div>
  )
}

export default App
