import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Phone, 
  Send, 
  RotateCcw, 
  Shield, 
  Info,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

const USSDSimulator = () => {
  const [sessionActive, setSessionActive] = useState(false)
  const [currentScreen, setCurrentScreen] = useState('')
  const [sessionData, setSessionData] = useState({})
  const [phoneNumber, setPhoneNumber] = useState('08012345678')
  const [userInput, setUserInput] = useState('')
  const [history, setHistory] = useState([])

  const addToHistory = (type, content) => {
    setHistory(prev => [...prev, { type, content, timestamp: new Date() }])
  }

  const startSession = () => {
    setSessionActive(true)
    setSessionData({})
    setHistory([])
    const welcomeScreen = `Welcome to GovTracka!
Citizen-led transparency platform

1. Report a project
2. Check report status
3. Data consent info
4. Delete my data
5. About GovTracka

Choose option:`

    setCurrentScreen(welcomeScreen)
    addToHistory('system', 'USSD session started')
    addToHistory('response', welcomeScreen)
  }

  const endSession = () => {
    setSessionActive(false)
    setCurrentScreen('')
    setSessionData({})
    addToHistory('system', 'USSD session ended')
  }

  const handleInput = (input) => {
    addToHistory('input', input)
    
    if (!sessionData.currentFlow) {
      // Main menu
      handleMainMenu(input)
    } else if (sessionData.currentFlow === 'report') {
      handleReportFlow(input)
    } else if (sessionData.currentFlow === 'status') {
      handleStatusFlow(input)
    } else if (sessionData.currentFlow === 'consent') {
      handleConsentFlow(input)
    } else if (sessionData.currentFlow === 'delete') {
      handleDeleteFlow(input)
    }
  }

  const handleMainMenu = (input) => {
    let response = ''
    
    switch(input) {
      case '1':
        setSessionData(prev => ({ ...prev, currentFlow: 'report' }))
        response = `Report a Project

Select project type:
1. School
2. Road
3. Clinic/Hospital
4. Water project
5. Bridge
6. Market
7. Other

Choose type:`
        break
        
      case '2':
        setSessionData(prev => ({ ...prev, currentFlow: 'status' }))
        response = `Check Report Status

Enter your phone number to see your reports:

(Format: 08012345678)`
        break
        
      case '3':
        setSessionData(prev => ({ ...prev, currentFlow: 'consent' }))
        response = `Data Consent Information

GovTracka processes your data to:
- Track government projects
- Fight corruption
- Improve transparency

Your data is stored securely in Nigeria.

1. Grant consent
2. View my consents
3. Withdraw consent

Choose:`
        break
        
      case '4':
        setSessionData(prev => ({ ...prev, currentFlow: 'delete' }))
        response = `Delete My Data

WARNING: This will permanently delete all your personal data from GovTracka.

Your project reports will remain public for transparency but will be anonymized.

1. Yes, delete my data
2. No, go back

Choose:`
        break
        
      case '5':
        response = `About GovTracka

GovTracka is a citizen-led platform for monitoring government projects and fighting corruption.

Features:
- Report project issues
- Verify project status
- Community voting
- NDPR compliant

Visit: www.govtracka.ng
Support: *347*0#

[Session will end]`
        setTimeout(() => endSession(), 3000)
        break
        
      default:
        response = `Invalid option. Please try again.

1. Report a project
2. Check report status
3. Data consent info
4. Delete my data
5. About GovTracka

Choose option:`
    }
    
    setCurrentScreen(response)
    addToHistory('response', response)
  }

  const handleReportFlow = (input) => {
    let response = ''
    const step = sessionData.reportStep || 'type'
    
    switch(step) {
      case 'type':
        const projectTypes = {
          '1': 'school',
          '2': 'road',
          '3': 'clinic',
          '4': 'water_project',
          '5': 'bridge',
          '6': 'market',
          '7': 'other'
        }
        
        if (projectTypes[input]) {
          setSessionData(prev => ({ 
            ...prev, 
            reportStep: 'name',
            projectType: projectTypes[input]
          }))
          response = `Project Name

Enter the name of the project:

(e.g., "Ikeja Primary School Block A")`
        } else {
          response = `Invalid selection.

Select project type:
1. School
2. Road
3. Clinic/Hospital
4. Water project
5. Bridge
6. Market
7. Other

Choose type:`
        }
        break
        
      case 'name':
        if (input.trim()) {
          setSessionData(prev => ({ 
            ...prev, 
            reportStep: 'location',
            projectName: input.trim()
          }))
          response = `Project Location

Enter the location/address:

(e.g., "Ikeja, Lagos State")`
        } else {
          response = `Project name cannot be empty.

Enter the name of the project:

(e.g., "Ikeja Primary School Block A")`
        }
        break
        
      case 'location':
        if (input.trim()) {
          setSessionData(prev => ({ 
            ...prev, 
            reportStep: 'description',
            location: input.trim()
          }))
          response = `Project Description

Describe the issue:

1. Not started
2. Incomplete/abandoned
3. Poor quality
4. Overpriced
5. Ghost project
6. Other issue

Choose:`
        } else {
          response = `Location cannot be empty.

Enter the location/address:

(e.g., "Ikeja, Lagos State")`
        }
        break
        
      case 'description':
        const descriptions = {
          '1': 'Project has not been started despite budget allocation',
          '2': 'Project is incomplete or has been abandoned',
          '3': 'Project quality is very poor or substandard',
          '4': 'Project appears to be overpriced for the work done',
          '5': 'This appears to be a ghost project (fake/non-existent)',
          '6': 'Other issues with this project'
        }
        
        if (descriptions[input]) {
          setSessionData(prev => ({ 
            ...prev, 
            reportStep: 'submit',
            description: descriptions[input]
          }))
          
          // Simulate submission
          const reportId = Math.random().toString(36).substr(2, 8)
          response = `Report Submitted Successfully!

Report ID: ${reportId}
Project: ${sessionData.projectName}
Status: Under Review

Your report will be verified by our community and NGO partners.

Thank you for fighting corruption!

Check status: *347*2#

[Session will end]`
          
          setTimeout(() => endSession(), 5000)
        } else {
          response = `Invalid selection.

Describe the issue:

1. Not started
2. Incomplete/abandoned
3. Poor quality
4. Overpriced
5. Ghost project
6. Other issue

Choose:`
        }
        break
    }
    
    setCurrentScreen(response)
    addToHistory('response', response)
  }

  const handleStatusFlow = (input) => {
    let response = ''
    
    if (input.length === 11 && input.startsWith('0')) {
      // Mock report status
      response = `Your Reports:

1. ✅ Ikeja School Project
2. ⏳ Lagos Road Repair
3. 🔍 Kano Hospital Wing

Legend:
⏳ Pending  🔍 Under Review
✅ Verified  ❌ Disputed

For details: www.govtracka.ng

[Session will end]`
      
      setTimeout(() => endSession(), 4000)
    } else {
      response = `Invalid phone number format.

Enter your phone number:

(Format: 08012345678)`
    }
    
    setCurrentScreen(response)
    addToHistory('response', response)
  }

  const handleConsentFlow = (input) => {
    let response = ''
    
    switch(input) {
      case '1':
        response = `Consent Granted!

You have consented to data processing for project reporting.

Your data will be:
- Stored securely in Nigeria
- Used only for transparency
- Anonymized when possible

Withdraw anytime: *347*9#

[Session will end]`
        setTimeout(() => endSession(), 4000)
        break
        
      case '2':
        response = `Your Active Consents:

• project_reporting: granted
• analytics: granted

To withdraw: *347*9#

[Session will end]`
        setTimeout(() => endSession(), 3000)
        break
        
      case '3':
        response = `Withdraw Consent

This will withdraw all your consents and anonymize your data.

1. Yes, withdraw all consents
2. No, go back

Choose:`
        setSessionData(prev => ({ ...prev, consentStep: 'withdraw' }))
        break
        
      default:
        if (sessionData.consentStep === 'withdraw') {
          if (input === '1') {
            response = `Consents Withdrawn!

All your consents have been withdrawn and your data has been anonymized.

Your project reports remain public for transparency but are no longer linked to you.

[Session will end]`
            setTimeout(() => endSession(), 4000)
          } else {
            // Go back to main consent menu
            setSessionData(prev => ({ ...prev, consentStep: null }))
            response = `Data Consent Information

GovTracka processes your data to:
- Track government projects
- Fight corruption
- Improve transparency

Your data is stored securely in Nigeria.

1. Grant consent
2. View my consents
3. Withdraw consent

Choose:`
          }
        } else {
          response = `Invalid selection.

1. Grant consent
2. View my consents
3. Withdraw consent

Choose:`
        }
    }
    
    setCurrentScreen(response)
    addToHistory('response', response)
  }

  const handleDeleteFlow = (input) => {
    let response = ''
    
    if (input === '1') {
      response = `Data Deleted Successfully!

Your personal data has been anonymized.

Your project reports remain public for transparency but are no longer linked to you.

Thank you for using GovTracka responsibly.

[Session will end]`
      setTimeout(() => endSession(), 4000)
    } else {
      // Go back to main menu
      setSessionData({ currentFlow: null })
      response = `Welcome to GovTracka!
Citizen-led transparency platform

1. Report a project
2. Check report status
3. Data consent info
4. Delete my data
5. About GovTracka

Choose option:`
    }
    
    setCurrentScreen(response)
    addToHistory('response', response)
  }

  const sendInput = () => {
    if (userInput.trim()) {
      handleInput(userInput.trim())
      setUserInput('')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">USSD Simulator</h1>
          <p className="text-gray-600 max-w-2xl mx-auto mb-6">
            Experience GovTracka's mobile interface. This simulator shows how citizens can 
            report corruption using any mobile phone via USSD code *347*#
          </p>
          
          <div className="flex justify-center space-x-2">
            <Badge className="bg-blue-100 text-blue-800">
              <Phone className="h-3 w-3 mr-1" />
              Works on Feature Phones
            </Badge>
            <Badge className="bg-green-100 text-green-800">
              <Shield className="h-3 w-3 mr-1" />
              NDPR Compliant
            </Badge>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Phone Simulator */}
          <div className="flex justify-center">
            <div className="relative">
              {/* Phone Frame */}
              <div className="w-80 h-96 bg-gray-900 rounded-3xl p-4 shadow-2xl">
                <div className="w-full h-full bg-black rounded-2xl p-4 font-mono text-green-400 text-sm overflow-hidden">
                  {/* Phone Header */}
                  <div className="text-center mb-4 text-green-300">
                    <div className="text-xs">📶 MTN NG    🔋 85%</div>
                    <div className="text-xs mt-1">*347*# - GovTracka</div>
                  </div>
                  
                  {/* Screen Content */}
                  <div className="h-64 overflow-y-auto whitespace-pre-wrap">
                    {sessionActive ? currentScreen : 'Dial *347*# to start'}
                  </div>
                  
                  {/* Input Area */}
                  {sessionActive && (
                    <div className="mt-4 border-t border-green-600 pt-2">
                      <div className="flex items-center">
                        <span className="text-green-300 mr-2">></span>
                        <input
                          type="text"
                          value={userInput}
                          onChange={(e) => setUserInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendInput()}
                          className="bg-transparent border-none outline-none text-green-400 flex-1"
                          placeholder="Type response..."
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Phone Controls */}
              <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 flex space-x-4">
                {!sessionActive ? (
                  <Button onClick={startSession} className="bg-green-600 hover:bg-green-700">
                    <Phone className="h-4 w-4 mr-2" />
                    Dial *347*#
                  </Button>
                ) : (
                  <>
                    <Button onClick={sendInput} size="sm">
                      <Send className="h-4 w-4 mr-2" />
                      Send
                    </Button>
                    <Button onClick={endSession} variant="outline" size="sm">
                      <RotateCcw className="h-4 w-4 mr-2" />
                      End Call
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Information Panel */}
          <div className="space-y-6">
            {/* Instructions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Info className="h-5 w-5 mr-2" />
                  How to Use
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">1</div>
                  <span>Click "Dial *347*#" to start the USSD session</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">2</div>
                  <span>Type numbers to navigate the menu (e.g., "1" for Report a project)</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">3</div>
                  <span>Follow the prompts to submit a corruption report</span>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">4</div>
                  <span>Press "End Call" to terminate the session</span>
                </div>
              </CardContent>
            </Card>

            {/* Features */}
            <Card>
              <CardHeader>
                <CardTitle>USSD Features</CardTitle>
                <CardDescription>What you can do via *347*#</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Report government project issues</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Check status of your reports</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Manage data consent (NDPR)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Request data deletion (*347*9#)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Works on any mobile phone</span>
                </div>
              </CardContent>
            </Card>

            {/* Session History */}
            {history.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Session History</CardTitle>
                  <CardDescription>Log of USSD interactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-48 overflow-y-auto text-xs">
                    {history.map((entry, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <span className="text-gray-500 text-xs">
                          {entry.timestamp.toLocaleTimeString()}
                        </span>
                        <span className={`font-medium ${
                          entry.type === 'input' ? 'text-blue-600' : 
                          entry.type === 'response' ? 'text-green-600' : 
                          'text-gray-600'
                        }`}>
                          {entry.type}:
                        </span>
                        <span className="text-gray-700 flex-1">
                          {entry.content.length > 50 ? 
                            entry.content.substring(0, 50) + '...' : 
                            entry.content
                          }
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Real Implementation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-orange-600">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  Real Implementation
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <p>In production, this USSD service would be integrated with:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  <li>Twilio or Africa's Talking USSD API</li>
                  <li>Nigerian telecom operators (MTN, Airtel, Glo, 9mobile)</li>
                  <li>USSD gateway providers</li>
                  <li>SMS notifications for status updates</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default USSDSimulator

