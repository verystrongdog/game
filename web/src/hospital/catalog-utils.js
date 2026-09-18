export function findAssetInstancePrefix(names, assetName) {
  const matchingName = names.find(name => name.toLowerCase().includes(assetName))
  return matchingName?.match(/^(\d{3})/)?.[1] || null
}
