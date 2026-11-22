param location string = 'eastus'

resource pricingStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg01'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg02'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg03'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg04'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg05'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg06'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg07'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg08'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg09'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg010'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

resource pricingStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'pricingstg011'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}
