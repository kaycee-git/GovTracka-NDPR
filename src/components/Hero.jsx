import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Shield, 
  MapPin, 
  Users, 
  TrendingUp,
  ArrowRight,
  Play
} from 'lucide-react'

const Hero = ({ setCurrentView }) => {
  return (
    <section className="relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-600 via-green-700 to-blue-800">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
              <div className="flex items-center space-x-4 mb-8">
                <Badge className="bg-green-100 text-green-800 hover:bg-green-200">
                  🇳🇬 Made for Nigeria
                </Badge>
                <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-200">
                  NDPA 2023 Compliant
                </Badge>
              </div>
            <h1 className="text-4xl lg:text-6xl font-bold leading-tight mb-6">
              Fight Corruption
              <span className="block text-green-300">One Report at a Time</span>
            </h1>

            <p className="text-xl lg:text-2xl text-green-100 mb-8 leading-relaxed">
              Empower yourself to monitor government projects, expose fraud, and ensure 
              transparency in public spending across Nigeria.
            </p>

            {/* Key Features */}
            <div className="grid sm:grid-cols-3 gap-4 mb-8">
              <div className="flex items-center">
                <Shield className="h-5 w-5 text-green-300 mr-2" />
                <span className="text-sm">NDPA 2023 Protected</span>
              </div>
              <div className="flex items-center">
                <MapPin className="h-5 w-5 text-green-300 mr-2" />
                <span className="text-sm">GPS Verified</span>
              </div>
              <div className="flex items-center">
                <Users className="h-5 w-5 text-green-300 mr-2" />
                <span className="text-sm">Community Driven</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg" 
                className="bg-white text-green-700 hover:bg-green-50 font-semibold"
                onClick={() => setCurrentView('report')}
              >
                Report a Project
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              
              <Button 
                size="lg" 
                variant="outline" 
                className="border-white text-white hover:bg-white hover:text-green-700"
                onClick={() => setCurrentView('transparency')}
              >
                <Play className="mr-2 h-5 w-5" />
                View Live Reports
              </Button>
            </div>

            {/* USSD Quick Access */}
            <div className="mt-8 p-4 bg-white bg-opacity-10 rounded-lg border border-white border-opacity-20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-100">Quick Access via USSD</p>
                  <p className="text-lg font-mono font-bold">*347*#</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="text-white hover:bg-white hover:text-green-700"
                  onClick={() => setCurrentView('ussd')}
                >
                  Try Now
                </Button>
              </div>
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            {/* Phone Mockup */}
            <div className="relative mx-auto w-64 h-96 bg-gray-900 rounded-3xl p-2 shadow-2xl">
              <div className="w-full h-full bg-white rounded-2xl overflow-hidden">
                {/* Phone Screen Content */}
                <div className="h-full bg-gradient-to-b from-green-50 to-white p-4">
                  <div className="text-center mb-4">
                    <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <h3 className="font-bold text-gray-900">GovTracka</h3>
                    <p className="text-xs text-gray-600">Report corruption instantly</p>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="bg-white rounded-lg p-3 shadow-sm border">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                        <span className="text-xs font-medium">Lagos School Project</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">Verified ✓</p>
                    </div>
                    
                    <div className="bg-white rounded-lg p-3 shadow-sm border">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                        <span className="text-xs font-medium">Abuja Road Project</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">Under Review</p>
                    </div>
                    
                    <div className="bg-white rounded-lg p-3 shadow-sm border">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                        <span className="text-xs font-medium">Kano Hospital</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">Disputed</p>
                    </div>
                  </div>
                  
                  <div className="mt-4 text-center">
                    <div className="bg-green-600 text-white rounded-lg py-2 px-4 text-xs font-medium">
                      Report New Project
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Stats */}
            <div className="absolute -top-4 -left-4 bg-white rounded-lg p-3 shadow-lg">
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 text-green-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Reports Today</p>
                  <p className="font-bold text-green-600">47</p>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-4 -right-4 bg-white rounded-lg p-3 shadow-lg">
              <div className="flex items-center">
                <Users className="h-4 w-4 text-blue-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Active Users</p>
                  <p className="font-bold text-blue-600">1.2K</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path 
            d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" 
            fill="white"
          />
        </svg>
      </div>
    </section>
  )
}

export default Hero

