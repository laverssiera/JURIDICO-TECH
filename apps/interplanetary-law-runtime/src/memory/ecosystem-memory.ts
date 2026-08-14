import Redis from "ioredis"

export class EcosystemMemory {
  private redis: Redis

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL ?? "redis://127.0.0.1:6379")
  }

  async storeLegalMemory(
    key: string,
    payload: unknown
  ) {
    await this.redis.set(
      `legal:${key}`,
      JSON.stringify(payload)
    )
  }

  async recoverLegalMemory(key: string) {
    const data = await this.redis.get(`legal:${key}`)

    if (!data) {
      return null
    }

    return JSON.parse(data)
  }
}