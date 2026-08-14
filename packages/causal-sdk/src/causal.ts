export interface CausalImpact {
  monolith: string
  effect: string
}

export interface CausalAssessment {
  regulation: string
  impacts: CausalImpact[]
}