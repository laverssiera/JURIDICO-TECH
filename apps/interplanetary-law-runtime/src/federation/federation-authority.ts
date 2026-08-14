import { connect, type NatsConnection } from "nats"

export class FederationAuthority {
  private nc?: NatsConnection

  async connect() {
    this.nc = await connect({
      servers: process.env.NATS_SERVERS ?? "nats://127.0.0.1:4222"
    })
  }

  async registerLegalRuntime() {
    if (!this.nc) {
      throw new Error("FederationAuthority is not connected")
    }

    await this.nc.publish(
      "federation.monolith.registered",
      Buffer.from(
        JSON.stringify({
          monolith: "JURIDICOTECH",
          type: "sovereign-legal-runtime"
        })
      )
    )
  }

  async synchronizeGovernance() {
    if (!this.nc) {
      throw new Error("FederationAuthority is not connected")
    }

    await this.nc.publish(
      "legal.governance.sync",
      Buffer.from(
        JSON.stringify({
          timestamp: Date.now()
        })
      )
    )
  }
}