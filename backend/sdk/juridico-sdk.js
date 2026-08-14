export class JuridicoSDK {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async createContract(data) {
    return fetch(`${this.baseUrl}/contracts`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-role": "SYSTEM_AUTOMATION" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  }

  async signContract(id, data = {}) {
    return fetch(`${this.baseUrl}/contracts/${id}/sign`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-role": "JURIDICO_ANALYST" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  }

  async analyzeRisk(data) {
    return fetch(`${this.baseUrl}/risk/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-role": "JURIDICO_ANALYST" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  }

  async protectRelationship(data) {
    return fetch(`${this.baseUrl}/bypass/protect`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-role": "SYSTEM_AUTOMATION" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  }

  async checkBypass(data) {
    return fetch(`${this.baseUrl}/bypass/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-user-role": "SYSTEM_AUTOMATION" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
  }
}
