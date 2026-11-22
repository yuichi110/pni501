param location string = 'eastus'

resource stockStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg01'
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

resource stockStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg02'
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

resource stockStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg03'
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

resource stockStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg04'
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

resource stockStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg05'
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

resource stockStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg06'
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

resource stockStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg07'
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

resource stockStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg08'
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

resource stockStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg09'
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

resource stockStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg010'
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

resource stockStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stockstg011'
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
