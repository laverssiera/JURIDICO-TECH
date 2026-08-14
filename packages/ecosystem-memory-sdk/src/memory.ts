export interface EcosystemMemoryRecord {
  key: string
  payload: unknown
  timestamp: number
}

export function createMemoryRecord(
  key: string,
  payload: unknown
): EcosystemMemoryRecord {
  return {
    key,
    payload,
    timestamp: Date.now()
  }
}