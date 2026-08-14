import neo4j, { type Driver } from "neo4j-driver"

export class LegalKnowledgeGraph {
  private driver: Driver

  constructor() {
    this.driver = neo4j.driver(
      process.env.NEO4J_URI ?? "bolt://127.0.0.1:7687",
      neo4j.auth.basic(
        process.env.NEO4J_USER ?? "neo4j",
        process.env.NEO4J_PASSWORD ?? "password"
      )
    )
  }

  async registerPatent(payload: {
    id: string
    title: string
    domain: string
    scope: string
  }) {
    const session = this.driver.session()

    try {
      await session.run(
        `
          MERGE (p:Patent {
            id: $id
          })

          SET p.title = $title,
              p.domain = $domain,
              p.scope = $scope,
              p.created_at = datetime()
        `,
        payload
      )
    } finally {
      await session.close()
    }
  }

  async connectPatentToResearch(
    patentId: string,
    researchId: string
  ) {
    const session = this.driver.session()

    try {
      await session.run(
        `
          MATCH (p:Patent {id: $patentId})
          MATCH (r:Research {id: $researchId})

          MERGE (p)-[:PROTECTS]->(r)
        `,
        {
          patentId,
          researchId
        }
      )
    } finally {
      await session.close()
    }
  }

  async close() {
    await this.driver.close()
  }
}