export interface PatentRecord {
  id: string
  title: string
  domain: string
  scope: string
}

export interface ResearchLink {
  patentId: string
  researchId: string
}