param location string = 'eastus'

resource ledgerStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg01'
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

resource ledgerStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg02'
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

resource ledgerStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg03'
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

resource ledgerStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg04'
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

resource ledgerStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg05'
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

resource ledgerStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg06'
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

resource ledgerStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg07'
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

resource ledgerStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg08'
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

resource ledgerStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg09'
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

resource ledgerStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg010'
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

resource ledgerStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'ledgerstg011'
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
