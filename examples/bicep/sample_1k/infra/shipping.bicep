param location string = 'eastus'

resource shipmentStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg01'
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

resource shipmentStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg02'
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

resource shipmentStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg03'
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

resource shipmentStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg04'
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

resource shipmentStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg05'
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

resource shipmentStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg06'
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

resource shipmentStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg07'
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

resource shipmentStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg08'
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

resource shipmentStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg09'
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

resource shipmentStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg010'
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

resource shipmentStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'shipmentstg011'
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
