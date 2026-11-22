param location string = 'eastus'

resource orderStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg01'
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

resource orderStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg02'
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

resource orderStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg03'
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

resource orderStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg04'
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

resource orderStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg05'
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

resource orderStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg06'
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

resource orderStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg07'
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

resource orderStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg08'
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

resource orderStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg09'
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

resource orderStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg010'
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

resource orderStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'orderstg011'
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
