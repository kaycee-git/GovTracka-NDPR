import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Shield, 
  Menu, 
  X, 
  Home, 
  BarChart3, 
  FileText, 
  Eye, 
  Phone 
} from 'lucide-react'

const Header = ({ currentView, setCurrentView }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Home', id: 'home', icon: Home },
    { name: 'Dashboard', id: 'dashboard', icon: BarChart3 },
    { name: 'Report Project', id: 'report', icon: FileText },
    { name: 'Transparency Feed', id: 'transparency', icon: Eye },
    { name: 'USSD Simulator', id: 'ussd', icon: Phone },
  ]

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <Shield className="h-8 w-8 text-green-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">GovTracka</span>
              <Badge variant="secondary" className="ml-2 text-xs">
                NDPA 2023 Compliant
              </Badge>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    currentView === item.id
                      ? 'text-green-600 bg-green-50'
                      : 'text-gray-700 hover:text-green-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {item.name}
                </button>
              )
            })}
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setCurrentView('login')}
            >
              Login
            </Button>
            <Button 
              size="sm"
              onClick={() => setCurrentView('signup')}
              className="bg-green-600 hover:bg-green-700"
            >
              Sign Up
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setCurrentView('ussd')}
            >
              Try USSD: *347*#
            </Button>
            <Button 
              size="sm"
              onClick={() => setCurrentView('report')}
            >
              Report Now
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-green-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setCurrentView(item.id)
                      setMobileMenuOpen(false)
                    }}
                    className={`flex items-center w-full px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ${
                      currentView === item.id
                        ? 'text-green-600 bg-green-50'
                        : 'text-gray-700 hover:text-green-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </button>
                )
              })}
              
              {/* Mobile CTA */}
              <div className="pt-4 space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    setCurrentView('ussd')
                    setMobileMenuOpen(false)
                  }}
                >
                  Try USSD: *347*#
                </Button>
                <Button 
                  className="w-full"
                  onClick={() => {
                    setCurrentView('report')
                    setMobileMenuOpen(false)
                  }}
                >
                  Report Now
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header

