declare module "node:crypto" {
  export function randomUUID(): string
}

declare module "nats" {
  export type NatsConnection = {
    publish(subject: string, payload: Uint8Array): Promise<void> | void
  }

  export function connect(options: {
    servers?: string | string[]
  }): Promise<NatsConnection>
}

declare module "neo4j-driver" {
  export type Driver = {
    session(): {
      run(query: string, params?: Record<string, unknown>): Promise<unknown>
      close(): Promise<void>
    }
    close(): Promise<void>
  }

  const neo4j: {
    driver(uri: string, auth: unknown): Driver
    auth: {
      basic(user: string, password: string): unknown
    }
  }

  export default neo4j
}

declare module "ioredis" {
  class Redis {
    constructor(url?: string)
    set(key: string, value: string): Promise<"OK">
    get(key: string): Promise<string | null>
  }

  export default Redis
}

declare module "prom-client" {
  class Registry {
    registerMetric(metric: unknown): void
    metrics(): Promise<string>
  }

  class Counter {
    constructor(options: unknown)
    inc(value?: number): void
  }

  const client: {
    Registry: typeof Registry
    Counter: typeof Counter
  }

  export default client
}

declare const Buffer: {
  from(value: string): Uint8Array
}

declare const process: {
  env: Record<string, string | undefined>
  exitCode?: number
}