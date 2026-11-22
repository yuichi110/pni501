param location string = 'eastus'

resource customerStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg01'
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

resource customerStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg02'
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

resource customerStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg03'
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

resource customerStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg04'
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

resource customerStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg05'
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

resource customerStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg06'
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

resource customerStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg07'
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

resource customerStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg08'
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

resource customerStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg09'
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

resource customerStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg010'
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

resource customerStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'customerstg011'
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
