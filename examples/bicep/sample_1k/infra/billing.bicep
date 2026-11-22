param location string = 'eastus'

resource invoiceStg1 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg01'
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

resource invoiceStg2 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg02'
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

resource invoiceStg3 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg03'
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

resource invoiceStg4 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg04'
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

resource invoiceStg5 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg05'
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

resource invoiceStg6 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg06'
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

resource invoiceStg7 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg07'
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

resource invoiceStg8 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg08'
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

resource invoiceStg9 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg09'
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

resource invoiceStg10 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg010'
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

resource invoiceStg11 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'invoicestg011'
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
