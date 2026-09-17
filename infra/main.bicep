targetScope = 'subscription'

@description('Deployment environment name. Use lowercase letters, numbers, and hyphens.')
@minLength(2)
@maxLength(24)
param environmentName string

@description('Azure region for all regional resources.')
param location string = 'eastus2'

@description('Digest-pinned application image to run in Container Apps. Set SERVICE_WEB_IMAGE explicitly before any facilitator deployment.')
@minLength(1)
param containerImage string

@description('Number of Container Apps replicas maintained during normal traffic.')
@minValue(1)
@maxValue(10)
param minReplicas int = 1

@description('Maximum Container Apps replicas permitted during a traffic spike.')
@minValue(1)
@maxValue(30)
param maxReplicas int = 3

@description('Retention period for operational logs.')
@minValue(30)
@maxValue(730)
param logRetentionInDays int = 90

@description('Provision Azure Communication Services. The application remains no-dispatch regardless of this setting.')
param enableCommunicationServices bool = false

@description('Azure Communication Services data location, not an Azure region.')
param communicationServicesDataLocation string = 'United States'

var normalizedEnvironmentName = toLower(replace(environmentName, '-', ''))
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var resourceGroupName = 'rg-cc-${environmentName}'
var resourcePrefix = 'cc-${environmentName}'
var acrName = take('cc${normalizedEnvironmentName}${resourceToken}', 50)
var storageAccountName = take('cc${normalizedEnvironmentName}${resourceToken}', 24)
var keyVaultName = take('kv-cc-${environmentName}-${resourceToken}', 24)
var cosmosAccountName = take('cosmos-cc-${environmentName}-${resourceToken}', 44)
var searchServiceName = take('srch-cc-${environmentName}-${resourceToken}', 60)
var tags = {
  application: 'constituent-connect'
  environment: environmentName
  dataClassification: 'synthetic'
  managedBy: 'bicep'
}

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module constituentConnect './modules/constituent-connect.bicep' = {
  name: 'constituent-connect-${environmentName}'
  scope: resourceGroup
  params: {
    location: location
    resourcePrefix: resourcePrefix
    resourceToken: resourceToken
    acrName: acrName
    storageAccountName: storageAccountName
    keyVaultName: keyVaultName
    cosmosAccountName: cosmosAccountName
    searchServiceName: searchServiceName
    containerImage: containerImage
    minReplicas: minReplicas
    maxReplicas: maxReplicas
    logRetentionInDays: logRetentionInDays
    enableCommunicationServices: enableCommunicationServices
    communicationServicesDataLocation: communicationServicesDataLocation
    tags: tags
  }
}

output resourceGroupName string = resourceGroup.name
output containerAppName string = constituentConnect.outputs.containerAppName
output containerAppUrl string = constituentConnect.outputs.containerAppUrl
output containerRegistryLoginServer string = constituentConnect.outputs.containerRegistryLoginServer
output keyVaultUri string = constituentConnect.outputs.keyVaultUri
output storageBlobEndpoint string = constituentConnect.outputs.storageBlobEndpoint
output cosmosEndpoint string = constituentConnect.outputs.cosmosEndpoint
output searchEndpoint string = constituentConnect.outputs.searchEndpoint
output applicationInsightsConnectionString string = constituentConnect.outputs.applicationInsightsConnectionString
