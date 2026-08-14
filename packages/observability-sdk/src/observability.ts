export interface ObservabilityEvent {
  name: string
  value: number
  labels?: Record<string, string>
}

export function createObservabilityEvent(
  name: string,
  value: number,
  labels: Record<string, string> = {}
): ObservabilityEvent {
  return {
    name,
    value,
    labels
  }
}