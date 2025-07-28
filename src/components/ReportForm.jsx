import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { 
  Camera, 
  MapPin, 
  Upload, 
  Shield, 
  AlertCircle,
  CheckCircle,
  FileText,
  DollarSign,
  Building,
  Phone,
  Loader2
} from 'lucide-react'

const ReportForm = () => {
  const [formData, setFormData] = useState({
    project_name: '',
    project_type: '',
    description: '',
    location_name: '',
    state: '',
    lga: '',
    reported_budget: '',
    contractor_name: '',
    submission_method: 'web'
  })
  
  const [files, setFiles] = useState([])
  const [location, setLocation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [errors, setErrors] = useState({})

  const projectTypes = [
    { value: 'school', label: 'School' },
    { value: 'road', label: 'Road' },
    { value: 'clinic', label: 'Clinic/Hospital' },
    { value: 'water_project', label: 'Water Project' },
    { value: 'bridge', label: 'Bridge' },
    { value: 'market', label: 'Market' },
    { value: 'other', label: 'Other' }
  ]

  const nigerianStates = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'FCT', 'Gombe',
    'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
    'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau',
    'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
  ]

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const handleFileUpload = (event) => {
    const selectedFiles = Array.from(event.target.files)
    setFiles(prev => [...prev, ...selectedFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (error) => {
          console.error('Error getting location:', error)
        }
      )
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.project_name.trim()) {
      newErrors.project_name = 'Project name is required'
    }
    
    if (!formData.project_type) {
      newErrors.project_type = 'Project type is required'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    }
    
    if (!formData.location_name.trim()) {
      newErrors.location_name = 'Location is required'
    }
    
    if (!formData.state) {
      newErrors.state = 'State is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock successful submission
      setSubmitted(true)
      
      // Reset form
      setFormData({
        project_name: '',
        project_type: '',
        description: '',
        location_name: '',
        state: '',
        lga: '',
        reported_budget: '',
        contractor_name: '',
        submission_method: 'web'
      })
      setFiles([])
      setLocation(null)
      
    } catch (error) {
      console.error('Submission error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-2xl mx-auto">
          <Card className="text-center">
            <CardContent className="pt-6">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Report Submitted Successfully!</h2>
              <p className="text-gray-600 mb-6">
                Your report has been received and will be verified by our community and NGO partners.
              </p>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-center mb-2">
                  <Shield className="h-5 w-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-800">NDPR Compliant</span>
                </div>
                <p className="text-sm text-green-700">
                  Your data is protected and stored securely in Nigeria. You can request deletion anytime via *347*9#
                </p>
              </div>

              <div className="space-y-3 text-sm text-gray-600 mb-6">
                <p>• Your report will be reviewed within 24-48 hours</p>
                <p>• Community members can vote on its accuracy</p>
                <p>• NGO partners will verify the information</p>
                <p>• You'll be notified of any updates</p>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button onClick={() => setSubmitted(false)}>
                  Submit Another Report
                </Button>
                <Button variant="outline">
                  View My Reports
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Report a Government Project</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Help fight corruption by reporting irregularities in government projects. 
            Your identity will be protected and data stored securely in Nigeria.
          </p>
          
          <div className="flex justify-center mt-4">
            <Badge className="bg-green-100 text-green-800">
              <Shield className="h-3 w-3 mr-1" />
              NDPR Compliant & Anonymous
            </Badge>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Main Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Project Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Building className="h-5 w-5 mr-2" />
                    Project Information
                  </CardTitle>
                  <CardDescription>
                    Provide details about the government project you want to report
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="project_name">Project Name *</Label>
                    <Input
                      id="project_name"
                      placeholder="e.g., Ikeja Primary School Block A"
                      value={formData.project_name}
                      onChange={(e) => handleInputChange('project_name', e.target.value)}
                      className={errors.project_name ? 'border-red-500' : ''}
                    />
                    {errors.project_name && (
                      <p className="text-sm text-red-600 mt-1">{errors.project_name}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="project_type">Project Type *</Label>
                    <Select value={formData.project_type} onValueChange={(value) => handleInputChange('project_type', value)}>
                      <SelectTrigger className={errors.project_type ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select project type" />
                      </SelectTrigger>
                      <SelectContent>
                        {projectTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.project_type && (
                      <p className="text-sm text-red-600 mt-1">{errors.project_type}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="description">Description of Issue *</Label>
                    <Textarea
                      id="description"
                      placeholder="Describe what's wrong with this project (e.g., not started, poor quality, overpriced, abandoned)"
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      rows={4}
                      className={errors.description ? 'border-red-500' : ''}
                    />
                    {errors.description && (
                      <p className="text-sm text-red-600 mt-1">{errors.description}</p>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="reported_budget">Project Budget (₦)</Label>
                      <Input
                        id="reported_budget"
                        type="number"
                        placeholder="e.g., 50000000"
                        value={formData.reported_budget}
                        onChange={(e) => handleInputChange('reported_budget', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="contractor_name">Contractor Name</Label>
                      <Input
                        id="contractor_name"
                        placeholder="e.g., ABC Construction Ltd"
                        value={formData.contractor_name}
                        onChange={(e) => handleInputChange('contractor_name', e.target.value)}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Location Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MapPin className="h-5 w-5 mr-2" />
                    Location Information
                  </CardTitle>
                  <CardDescription>
                    Specify where this project is located
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="location_name">Location/Address *</Label>
                    <Input
                      id="location_name"
                      placeholder="e.g., Ikeja, Lagos State"
                      value={formData.location_name}
                      onChange={(e) => handleInputChange('location_name', e.target.value)}
                      className={errors.location_name ? 'border-red-500' : ''}
                    />
                    {errors.location_name && (
                      <p className="text-sm text-red-600 mt-1">{errors.location_name}</p>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="state">State *</Label>
                      <Select value={formData.state} onValueChange={(value) => handleInputChange('state', value)}>
                        <SelectTrigger className={errors.state ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Select state" />
                        </SelectTrigger>
                        <SelectContent>
                          {nigerianStates.map((state) => (
                            <SelectItem key={state} value={state}>
                              {state}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {errors.state && (
                        <p className="text-sm text-red-600 mt-1">{errors.state}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="lga">Local Government Area</Label>
                      <Input
                        id="lga"
                        placeholder="e.g., Ikeja"
                        value={formData.lga}
                        onChange={(e) => handleInputChange('lga', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button type="button" variant="outline" onClick={getLocation}>
                      <MapPin className="h-4 w-4 mr-2" />
                      Get Current Location
                    </Button>
                    {location && (
                      <Badge variant="secondary">
                        GPS: {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Evidence Upload */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Camera className="h-5 w-5 mr-2" />
                    Evidence Files
                  </CardTitle>
                  <CardDescription>
                    Upload photos, videos, or documents as evidence
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600 mb-2">
                      Drag and drop files here, or click to select
                    </p>
                    <input
                      type="file"
                      multiple
                      accept="image/*,video/*,.pdf,.doc,.docx"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload">
                      <Button type="button" variant="outline" size="sm">
                        Choose Files
                      </Button>
                    </label>
                  </div>

                  {files.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm text-gray-700">{file.name}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(index)}
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* NDPR Notice */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-green-600">
                    <Shield className="h-5 w-5 mr-2" />
                    Data Protection
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span>Data stored securely in Nigeria</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span>Automatic face anonymization</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span>Right to be forgotten (*347*9#)</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span>NDPR compliant processing</span>
                  </div>
                </CardContent>
              </Card>

              {/* USSD Alternative */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-blue-600">
                    <Phone className="h-5 w-5 mr-2" />
                    Mobile Access
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm">
                  <p className="mb-3">No internet? Use USSD:</p>
                  <div className="bg-blue-50 p-3 rounded text-center">
                    <span className="font-mono font-bold text-lg">*347*#</span>
                  </div>
                  <p className="mt-2 text-gray-600">
                    Works on any mobile phone, even feature phones
                  </p>
                </CardContent>
              </Card>

              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    Submit Report
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ReportForm

