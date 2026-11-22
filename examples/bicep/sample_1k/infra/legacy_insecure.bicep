param location string = 'eastus'
resource legacyStg 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'legacystg01'
  location: location
  properties: {
    supportsHttpsTrafficOnly: false
    allowBlobPublicAccess: true
  }
}
